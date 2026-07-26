// Heat-Town PoC — Leaflet viewer
// scores.geojson を読み、Ji を色分け表示。重み変更でクライアント側再計算。

const PRESETS = {
    balanced: { w1: 0.3, w2: 0.4, w3: 0.3 },
    elderly: { w1: 0.2, w2: 0.5, w3: 0.3 },
    commuter: { w1: 0.5, w2: 0.2, w3: 0.3 },
    heat_alert: { w1: 0.2, w2: 0.2, w3: 0.6 },
};

const COLORS = ["#2a9d8f", "#8bc34a", "#ffb03b", "#f4813f", "#e63946"];

let features = [];
let layer = null;
let map = null;

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    })[char]);
}

function normalizeFeatures(rawFeatures) {
    return rawFeatures.map((feature, index) => {
        const props = feature.properties ?? {};
        const d = Number(props.distance ?? props.d ?? props.distance_norm ?? 0);
        const comfort = Number(props.comfort ?? props.C ?? 0);
        const wbgt = Number(props.wbgt ?? props.WBGT ?? 0);
        return {
            ...feature,
            properties: {
                ...props,
                name: props.name ?? `地点 ${index + 1}`,
                district: props.district ?? "",
                distance: d,
                comfort,
                wbgt,
            },
        };
    });
}

function normalizeWeights(w) {
    const total = w.w1 + w.w2 + w.w3;
    if (total <= 0) {
        return { ...PRESETS.balanced };
    }
    return { w1: w.w1 / total, w2: w.w2 / total, w3: w.w3 / total };
}

function quantile(sortedValues, fraction) {
    if (sortedValues.length === 0) return 0;
    if (sortedValues.length === 1) return sortedValues[0];
    const index = (sortedValues.length - 1) * fraction;
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    if (lower === upper) return sortedValues[lower];
    return sortedValues[lower] + (sortedValues[upper] - sortedValues[lower]) * (index - lower);
}

function scoreColor(ji, breaks) {
    if (ji <= breaks[0]) return COLORS[0];
    if (ji <= breaks[1]) return COLORS[1];
    if (ji <= breaks[2]) return COLORS[2];
    if (ji <= breaks[3]) return COLORS[3];
    return COLORS[4];
}

function recompute(props, w) {
    const nw = normalizeWeights(w);
    const distance = nw.w1 * props.distance;
    const discomfort = nw.w2 * (100 - props.comfort);
    const heat = nw.w3 * props.wbgt;
    return { ji: distance + discomfort + heat, distance, discomfort, heat };
}

function currentWeights() {
    return {
        w1: parseFloat(document.getElementById("w1").value),
        w2: parseFloat(document.getElementById("w2").value),
        w3: parseFloat(document.getElementById("w3").value),
    };
}

function updateStatus(message) {
    const el = document.getElementById("status");
    if (el) el.textContent = message;
}

function popupHtml(f, r) {
    const { name, district } = f.properties;
    const title = escapeHtml(name);
    const districtHtml = district ? ` <small>(${escapeHtml(district)})</small>` : "";
    const parts = [
        ["距離", r.distance, "#2a9d8f"],
        ["不快", r.discomfort, "#f4813f"],
        ["暑さ", r.heat, "#e63946"],
    ];
    const maxc = Math.max(...parts.map((p) => p[1]), 0.01);
    let html = `<b>${title}${districtHtml}</b><br/><b>Jᵢ = ${r.ji.toFixed(1)}</b><br/><small>低いほど安全</small><hr/>`;
    for (const [label, val, col] of parts) {
        const pct = (val / maxc) * 100;
        html += `${label}: ${val.toFixed(1)}
      <div class="contrib-bar" style="width:${pct}%;background:${col}"></div>`;
    }
    return html;
}

function render() {
    if (!features.length) {
        updateStatus("表示する地点がありません。pipeline --sample を実行してください。");
        return;
    }

    const w = currentWeights();
    const nw = normalizeWeights(w);
    const recomputed = features.map((f) => ({
        f,
        r: recompute(f.properties, w),
    }));
    const jis = recomputed.map((x) => x.r.ji).sort((a, b) => a - b);
    const breaks = [0.2, 0.4, 0.6, 0.8].map((f) => quantile(jis, f));

    if (layer) map.removeLayer(layer);
    layer = L.layerGroup(
        recomputed.map(({ f, r }) => {
            const [lon, lat] = f.geometry.coordinates;
            const m = L.circleMarker([lat, lon], {
                radius: 6,
                color: "#333",
                weight: 0.5,
                fillColor: scoreColor(r.ji, breaks),
                fillOpacity: 0.8,
            });
            m.bindPopup(popupHtml(f, r));
            return m;
        })
    ).addTo(map);

    renderLegend(breaks);
    updateStatus(
        `${features.length} 点 | w₁=${nw.w1.toFixed(2)} w₂=${nw.w2.toFixed(2)} w₃=${nw.w3.toFixed(2)}`
    );
}

function renderLegend(breaks) {
    const el = document.getElementById("legend");
    const labels = [
        `≤ ${breaks[0].toFixed(0)}`,
        `${breaks[0].toFixed(0)}–${breaks[1].toFixed(0)}`,
        `${breaks[1].toFixed(0)}–${breaks[2].toFixed(0)}`,
        `${breaks[2].toFixed(0)}–${breaks[3].toFixed(0)}`,
        `≥ ${breaks[3].toFixed(0)}`,
    ];
    el.innerHTML = labels
        .map(
            (label, i) =>
                `<div><i style="background:${COLORS[i]}"></i>${label}</div>`
        )
        .join("");
}

function syncLabels() {
    for (const k of ["w1", "w2", "w3"]) {
        document.getElementById(k + "v").textContent =
            parseFloat(document.getElementById(k).value).toFixed(2);
    }
}

function setWeights(w) {
    document.getElementById("w1").value = w.w1;
    document.getElementById("w2").value = w.w2;
    document.getElementById("w3").value = w.w3;
    syncLabels();
    render();
}

async function init() {
    map = L.map("map");
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
        maxZoom: 19,
    }).addTo(map);

    updateStatus("scores.geojson を読み込み中…");

    try {
        const res = await fetch("data/scores.geojson", { cache: "no-store" });
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        const geo = await res.json();
        features = normalizeFeatures(Array.isArray(geo.features) ? geo.features : []);
        if (!features.length) {
            throw new Error("Feature が 0 件です");
        }
    } catch (e) {
        const msg =
            "scores.geojson を読み込めません。`python -m heat_town.cli pipeline --sample` を実行してください。";
        updateStatus(msg);
        alert(msg);
        return;
    }

    const lats = features.map((f) => f.geometry.coordinates[1]);
    const lons = features.map((f) => f.geometry.coordinates[0]);
    map.fitBounds([
        [Math.min(...lats), Math.min(...lons)],
        [Math.max(...lats), Math.max(...lons)],
    ]);

    for (const k of ["w1", "w2", "w3"]) {
        document.getElementById(k).addEventListener("input", () => {
            syncLabels();
            render();
            document.querySelectorAll(".presets button").forEach((b) => b.classList.remove("active"));
        });
    }
    document.querySelectorAll(".presets button").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".presets button").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            setWeights(PRESETS[btn.dataset.preset]);
        });
    });

    render();
}

init();
