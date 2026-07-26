// Heat-Town PoC — Leaflet viewer
// scores.geojson を読み、Ji を色分け表示。重み変更でクライアント側再計算。

const PRESETS = {
    balanced: { w1: 0.3, w2: 0.4, w3: 0.3 },
    elderly: { w1: 0.2, w2: 0.5, w3: 0.3 },
    commuter: { w1: 0.5, w2: 0.2, w3: 0.3 },
    heat_alert: { w1: 0.2, w2: 0.2, w3: 0.6 },
};

let features = [];
let layer = null;
let map = null;

// Ji を色に変換（低い=緑=安全, 高い=赤=危険）
function jiColor(ji, min, max) {
    const t = max > min ? (ji - min) / (max - min) : 0.5;
    const hue = (1 - t) * 120; // 120=緑 → 0=赤
    return `hsl(${hue}, 75%, 50%)`;
}

// 正規化した重みで Ji と寄与を再計算
function recompute(props, w) {
    const total = w.w1 + w.w2 + w.w3 || 1;
    const n1 = w.w1 / total, n2 = w.w2 / total, n3 = w.w3 / total;
    const distance = n1 * props.distance;
    const discomfort = n2 * (100 - props.comfort);
    const heat = n3 * props.wbgt;
    return { ji: distance + discomfort + heat, distance, discomfort, heat };
}

function currentWeights() {
    return {
        w1: parseFloat(document.getElementById("w1").value),
        w2: parseFloat(document.getElementById("w2").value),
        w3: parseFloat(document.getElementById("w3").value),
    };
}

function popupHtml(r) {
    const parts = [
        ["距離", r.distance, "#2a9d8f"],
        ["不快", r.discomfort, "#f4813f"],
        ["暑さ", r.heat, "#e63946"],
    ];
    const maxc = Math.max(...parts.map((p) => p[1]), 0.01);
    let html = `<b>Jᵢ = ${r.ji.toFixed(1)}</b><br/><small>低いほど安全</small><hr/>`;
    for (const [name, val, col] of parts) {
        const pct = (val / maxc) * 100;
        html += `${name}: ${val.toFixed(1)}
      <div class="contrib-bar" style="width:${pct}%;background:${col}"></div>`;
    }
    return html;
}

function render() {
    const w = currentWeights();
    const recomputed = features.map((f) => ({
        f,
        r: recompute(f.properties, w),
    }));
    const jis = recomputed.map((x) => x.r.ji);
    const min = Math.min(...jis), max = Math.max(...jis);

    if (layer) map.removeLayer(layer);
    layer = L.layerGroup(
        recomputed.map(({ f, r }) => {
            const [lon, lat] = f.geometry.coordinates;
            const m = L.circleMarker([lat, lon], {
                radius: 6,
                color: "#333",
                weight: 0.5,
                fillColor: jiColor(r.ji, min, max),
                fillOpacity: 0.8,
            });
            m.bindPopup(popupHtml(r));
            return m;
        })
    ).addTo(map);

    renderLegend(min, max);
}

function renderLegend(min, max) {
    const el = document.getElementById("legend");
    const steps = 5;
    let html = "";
    for (let i = 0; i < steps; i++) {
        const ji = min + ((max - min) * i) / (steps - 1);
        html += `<div><i style="background:${jiColor(ji, min, max)}"></i>${ji.toFixed(0)}</div>`;
    }
    el.innerHTML = html;
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

    try {
        const res = await fetch("data/scores.geojson");
        const geo = await res.json();
        features = geo.features;
    } catch (e) {
        alert("scores.geojson を読み込めません。src/export で生成してください。");
        return;
    }

    // 地図の中心・ズームをデータ範囲に合わせる
    const lats = features.map((f) => f.geometry.coordinates[1]);
    const lons = features.map((f) => f.geometry.coordinates[0]);
    const bounds = [
        [Math.min(...lats), Math.min(...lons)],
        [Math.max(...lats), Math.max(...lons)],
    ];
    map.fitBounds(bounds);

    // スライダー
    for (const k of ["w1", "w2", "w3"]) {
        document.getElementById(k).addEventListener("input", () => {
            syncLabels();
            render();
            document.querySelectorAll(".presets button").forEach((b) => b.classList.remove("active"));
        });
    }
    // プリセット
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