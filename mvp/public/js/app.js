// Heat-Town — Rest-first UX (Primary) + Analysis mode (Secondary)
// Primary: geolocation → Top-3 rest spots + Google Maps nav
// Secondary: 400-point grid J_i visualization with weight sliders

const PRESETS = {
    balanced: { w1: 0.3, w2: 0.4, w3: 0.3 },
    elderly: { w1: 0.2, w2: 0.5, w3: 0.3 },
    commuter: { w1: 0.5, w2: 0.2, w3: 0.3 },
    heat_alert: { w1: 0.2, w2: 0.2, w3: 0.6 },
};

const COLORS = ["#2a9d8f", "#8bc34a", "#ffb03b", "#f4813f", "#e63946"];
const POI_COLORS = { park: "#2a9d8f", tree: "#8bc34a", shade_building: "#5b9bd5" };
const POI_RANK_COLORS = ["#2a9d8f", "#8bc34a", "#ffb03b"];

const ARIAKE_CENTER = { lat: 35.634, lon: 139.790 };
const DEFAULT_USER = ARIAKE_CENTER;
const SERVICE_AREA_RADIUS_M = 1500;
const DEMO_BANNER_TEXT =
    "📍 デモ表示: 有明キャンパス（現在地がエリア外のため自動補正中）";
const WALK_SPEED_M_PER_MIN = 80;
const MAX_WALK_M = 800;

const KIND_LABELS = { park: "公園", tree: "街路樹", shade_building: "ビル影" };

let gridFeatures = [];
let poiCandidates = [];
let restMeta = {};
let gridLayer = null;
let poiLayer = null;
let userMarker = null;
let map = null;
let userLocation = null;
/** Google Maps ナビの起点（デモ時は有明に固定） */
let currentOrigin = { ...ARIAKE_CENTER };
let clickToSetMode = false;

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    })[char]);
}

function normalizeWeights(w) {
    const total = w.w1 + w.w2 + w.w3;
    if (total <= 0) return { ...PRESETS.balanced };
    return { w1: w.w1 / total, w2: w.w2 / total, w3: w.w3 / total };
}

function haversineM(lat1, lon1, lat2, lon2) {
    const r = 6371000;
    const p1 = (lat1 * Math.PI) / 180;
    const p2 = (lat2 * Math.PI) / 180;
    const dp = ((lat2 - lat1) * Math.PI) / 180;
    const dl = ((lon2 - lon1) * Math.PI) / 180;
    const a =
        Math.sin(dp / 2) ** 2 +
        Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
    return 2 * r * Math.asin(Math.sqrt(Math.min(a, 1)));
}

function computeJi(d, comfort, wbgt, w) {
    const nw = normalizeWeights(w);
    return nw.w1 * d + nw.w2 * (100 - comfort) + nw.w3 * wbgt;
}

function comfortStatus(comfort) {
    if (comfort >= 85) return "快適";
    if (comfort >= 70) return "やや快適";
    if (comfort >= 55) return "普通";
    return "注意";
}

function isDemoMode() {
    return new URLSearchParams(window.location.search).get("demo") === "1";
}

function isInServiceArea(lat, lon, center = ARIAKE_CENTER, radiusM = SERVICE_AREA_RADIUS_M) {
    return haversineM(lat, lon, center.lat, center.lon) <= radiusM;
}

function resolveUserLocation(gpsLat, gpsLon, demoMode = isDemoMode()) {
    const meta = restMeta.service_area ?? {};
    const center = {
        lat: meta.center?.latitude ?? ARIAKE_CENTER.lat,
        lon: meta.center?.longitude ?? ARIAKE_CENTER.lon,
    };
    const radiusM = meta.radius_m ?? SERVICE_AREA_RADIUS_M;

    if (demoMode || !isInServiceArea(gpsLat, gpsLon, center, radiusM)) {
        return {
            lat: center.lat,
            lon: center.lon,
            source: demoMode ? "demo-forced" : "out-of-area-fallback",
            corrected: true,
            bannerMessage: DEMO_BANNER_TEXT,
        };
    }
    return { lat: gpsLat, lon: gpsLon, source: "gps", corrected: false, bannerMessage: null };
}

function updateNavOrigin(searchLat, searchLon, locationMeta = {}, emptyFallback = false) {
    if (isDemoMode() || locationMeta.corrected || emptyFallback) {
        currentOrigin = { lat: ARIAKE_CENTER.lat, lon: ARIAKE_CENTER.lon };
        return;
    }
    currentOrigin = { lat: searchLat, lon: searchLon };
}

function showLocationBanner(message) {
    const el = document.getElementById("location-banner");
    if (!el) return;
    el.hidden = false;
    el.textContent = message;
}

function hideLocationBanner() {
    const el = document.getElementById("location-banner");
    if (el) el.hidden = true;
}

function googleMapsUrl(destLat, destLon, origin = currentOrigin) {
    return (
        `https://www.google.com/maps/dir/?api=1` +
        `&origin=${origin.lat.toFixed(6)},${origin.lon.toFixed(6)}` +
        `&destination=${destLat.toFixed(6)},${destLon.toFixed(6)}` +
        `&travelmode=walking`
    );
}

function findRestSpotsWithFallback(userLat, userLon, weights, k = 3, maxWalkM = MAX_WALK_M) {
    let spots = findRestSpots(userLat, userLon, poiCandidates, weights, k, maxWalkM);
    if (spots.length > 0) {
        return { spots, emptyFallback: false };
    }
    spots = findRestSpots(
        ARIAKE_CENTER.lat,
        ARIAKE_CENTER.lon,
        poiCandidates,
        weights,
        k,
        maxWalkM
    );
    return { spots, emptyFallback: true };
}

function findRestSpots(userLat, userLon, pois, weights, k = 3, maxWalkM = MAX_WALK_M) {
    const wbgt = restMeta.wbgt ?? 28;
    const candidates = [];

    for (const poi of pois) {
        const [lon, lat] = poi.geometry.coordinates;
        const props = poi.properties ?? {};
        const distM = haversineM(userLat, userLon, lat, lon);
        if (distM > maxWalkM) continue;

        const comfort = Number(props.comfort ?? 70);
        const dNorm = Math.min(distM / maxWalkM, 1);
        const ji = computeJi(dNorm, comfort, wbgt, weights);
        const score = 0.6 * dNorm + 0.4 * (ji / 100);

        candidates.push({
            rank: 0,
            name: props.name ?? KIND_LABELS[props.kind] ?? "涼み場",
            kind: props.kind ?? "tree",
            kindLabel: props.kind_label ?? KIND_LABELS[props.kind] ?? props.kind,
            lat,
            lon,
            distanceM: Math.round(distM * 10) / 10,
            walkMin: Math.round((distM / WALK_SPEED_M_PER_MIN) * 10) / 10,
            comfort: Math.round(comfort * 10) / 10,
            comfortStatus: comfortStatus(comfort),
            jiScore: Math.round(ji * 100) / 100,
            score,
            mapsUrl: googleMapsUrl(lat, lon),
        });
    }

    candidates.sort((a, b) => a.score - b.score || a.distanceM - b.distanceM);
    return candidates.slice(0, k).map((s, i) => ({ ...s, rank: i + 1 }));
}

function normalizeGridFeatures(rawFeatures) {
    return rawFeatures.map((feature, index) => {
        const props = feature.properties ?? {};
        const d = Number(props.distance ?? props.d ?? 0);
        const comfort = Number(props.comfort ?? props.C ?? 0);
        const wbgt = Number(props.wbgt ?? props.WBGT ?? 0);
        return {
            ...feature,
            properties: {
                ...props,
                name: props.name ?? `格子 ${index + 1}`,
                distance: d,
                comfort,
                wbgt,
            },
        };
    });
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

function updateWbgtBanner() {
    const el = document.getElementById("wbgt-banner");
    const wbgt = restMeta.wbgt ?? gridFeatures[0]?.properties?.wbgt ?? null;
    if (!el || wbgt == null) return;

    let level = "注意";
    if (wbgt >= 31) level = "危険（運動中止）";
    else if (wbgt >= 28) level = "厳重警戒";
    else if (wbgt >= 25) level = "警戒";

    el.hidden = false;
    el.innerHTML = `<strong>🌡 WBGT ${Number(wbgt).toFixed(1)}</strong> — ${level}<br><small>エリア共通の推定値（公式観測ではありません）</small>`;
}

function renderSpotCards(spots) {
    const list = document.getElementById("spot-list");
    if (!list) return;

    list.innerHTML = spots
        .map((s) => {
            const badgeClass = s.comfort >= 70 ? "comfort-badge" : "comfort-badge warn";
            return `
        <article class="spot-card rank-${s.rank}">
          <div class="rank">第 ${s.rank} 候補</div>
          <div class="name">${escapeHtml(s.name)}</div>
          <div class="meta">
            ${escapeHtml(s.kindLabel)} · 徒歩約 ${s.walkMin} 分（${Math.round(s.distanceM)}m）<br>
            <span class="${badgeClass}">${escapeHtml(s.comfortStatus)}</span>
            · Jᵢ ${s.jiScore.toFixed(1)}
          </div>
          <a class="nav-btn" href="${escapeHtml(s.mapsUrl)}" target="_blank" rel="noopener noreferrer">
            🧭 Google Maps でナビ起動
          </a>
        </article>`;
        })
        .join("");
}

function renderPoiPins(spots) {
    if (poiLayer) map.removeLayer(poiLayer);

    poiLayer = L.layerGroup(
        spots.map((s) => {
            const color = POI_RANK_COLORS[s.rank - 1] ?? POI_COLORS[s.kind] ?? "#2a9d8f";
            const marker = L.circleMarker([s.lat, s.lon], {
                radius: 14 - s.rank * 2,
                color: "#fff",
                weight: 2,
                fillColor: color,
                fillOpacity: 0.95,
            });
            marker.bindPopup(
                `<b>${escapeHtml(s.name)}</b><br>${escapeHtml(s.kindLabel)}<br>徒歩 ${s.walkMin} 分`
            );
            return marker;
        })
    ).addTo(map);

    if (spots.length) {
        const bounds = spots.map((s) => [s.lat, s.lon]);
        if (userLocation) bounds.push([userLocation.lat, userLocation.lon]);
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
    }
}

function setUserMarker(lat, lon, label = "現在地") {
    if (userMarker) map.removeLayer(userMarker);
    const icon = L.divIcon({
        className: "user-marker-wrap",
        html: '<div class="user-marker" style="width:14px;height:14px;"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7],
    });
    userMarker = L.marker([lat, lon], { icon, zIndexOffset: 1000 }).addTo(map);
    userMarker.bindPopup(label);
}

function searchRestSpots(lat, lon, sourceLabel, locationMeta = {}) {
    const weights = currentWeights();
    const { spots, emptyFallback } = findRestSpotsWithFallback(lat, lon, weights);

    if (locationMeta.bannerMessage) {
        showLocationBanner(locationMeta.bannerMessage);
    } else if (emptyFallback) {
        showLocationBanner(DEMO_BANNER_TEXT);
    } else {
        hideLocationBanner();
    }

    const displayLat = emptyFallback ? ARIAKE_CENTER.lat : lat;
    const displayLon = emptyFallback ? ARIAKE_CENTER.lon : lon;
    updateNavOrigin(displayLat, displayLon, locationMeta, emptyFallback);

    // mapsUrl を currentOrigin 反映後に再生成
    const spotsWithNav = spots.map((s) => ({
        ...s,
        mapsUrl: googleMapsUrl(s.lat, s.lon),
    }));

    userLocation = { lat: displayLat, lon: displayLon };
    setUserMarker(displayLat, displayLon, locationMeta.source === "playground" ? "仮想現在地" : "現在地");
    renderSpotCards(spotsWithNav);

    const label = emptyFallback ? "有明キャンパス（候補なしフォールバック）" : sourceLabel;
    renderPoiPins(spotsWithNav);
    updateStatus(`${label} — ${spotsWithNav.length} 件の涼み場（800m 以内）`);
}

function popupHtml(f, r) {
    const { name } = f.properties;
    const title = escapeHtml(name);
    const parts = [
        ["距離", r.distance, "#2a9d8f"],
        ["不快", r.discomfort, "#f4813f"],
        ["暑さ", r.heat, "#e63946"],
    ];
    const maxc = Math.max(...parts.map((p) => p[1]), 0.01);
    let html = `<b>${title}</b><br/><b>Jᵢ = ${r.ji.toFixed(1)}</b><br/><small>低いほど安全</small><hr/>`;
    for (const [label, val, col] of parts) {
        const pct = (val / maxc) * 100;
        html += `${label}: ${val.toFixed(1)}
      <div class="contrib-bar" style="width:${pct}%;background:${col}"></div>`;
    }
    return html;
}

function renderGrid() {
    const showGrid = document.getElementById("show-grid")?.checked;
    if (gridLayer) {
        map.removeLayer(gridLayer);
        gridLayer = null;
    }
    if (!showGrid || !gridFeatures.length) {
        renderDangerList([]);
        renderLegend([]);
        return;
    }

    const w = currentWeights();
    const recomputed = gridFeatures.map((f) => ({ f, r: recompute(f.properties, w) }));
    const jis = recomputed.map((x) => x.r.ji).sort((a, b) => a - b);
    const breaks = [0.2, 0.4, 0.6, 0.8].map((f) => quantile(jis, f));

    gridLayer = L.layerGroup(
        recomputed.map(({ f, r }) => {
            const [lon, lat] = f.geometry.coordinates;
            const m = L.circleMarker([lat, lon], {
                radius: 5,
                color: "#333",
                weight: 0.5,
                fillColor: scoreColor(r.ji, breaks),
                fillOpacity: 0.75,
            });
            m.bindPopup(popupHtml(f, r));
            return m;
        })
    ).addTo(map);

    renderLegend(breaks);
    renderDangerList(recomputed);
}

function renderLegend(breaks) {
    const el = document.getElementById("legend");
    if (!el) return;
    if (!breaks.length) {
        el.innerHTML = "";
        return;
    }
    const labels = [
        `≤ ${breaks[0].toFixed(0)}`,
        `${breaks[0].toFixed(0)}–${breaks[1].toFixed(0)}`,
        `${breaks[1].toFixed(0)}–${breaks[2].toFixed(0)}`,
        `${breaks[2].toFixed(0)}–${breaks[3].toFixed(0)}`,
        `≥ ${breaks[3].toFixed(0)}`,
    ];
    el.innerHTML = labels
        .map((label, i) => `<div><i style="background:${COLORS[i]}"></i>${label}</div>`)
        .join("");
}

function renderDangerList(recomputed) {
    const el = document.getElementById("danger-list");
    if (!el) return;
    if (!recomputed.length) {
        el.innerHTML = "<li>格子表示を ON にすると表示されます</li>";
        return;
    }
    const top = [...recomputed].sort((a, b) => b.r.ji - a.r.ji).slice(0, 10);
    el.innerHTML = top
        .map(
            ({ f, r }, i) =>
                `<li>${i + 1}. ${escapeHtml(f.properties.name)} — Jᵢ ${r.ji.toFixed(1)}</li>`
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
    renderGrid();
    if (userLocation) {
        searchRestSpots(userLocation.lat, userLocation.lon, "重み変更後");
    }
}

function resetToAriake() {
    clickToSetMode = false;
    const btn = document.getElementById("playground-toggle");
    if (btn) {
        btn.classList.remove("active");
        btn.textContent = "🕹️ クリック位置を現在地にする";
    }
    if (map) map.getContainer().style.cursor = "";
    const resolved = resolveUserLocation(ARIAKE_CENTER.lat, ARIAKE_CENTER.lon, isDemoMode());
    searchRestSpots(resolved.lat, resolved.lon, "有明キャンパス（初期位置）", resolved);
}

function toggleClickToSetMode() {
    clickToSetMode = !clickToSetMode;
    const btn = document.getElementById("playground-toggle");
    if (!btn || !map) return;
    if (clickToSetMode) {
        btn.classList.add("active");
        btn.textContent = "🕹️ クリックモード ON（地図をタップ）";
        map.getContainer().style.cursor = "crosshair";
        updateStatus("地図をクリックすると、その位置を仮の現在地に設定します");
    } else {
        btn.classList.remove("active");
        btn.textContent = "🕹️ クリック位置を現在地にする";
        map.getContainer().style.cursor = "";
        updateStatus("クリックモード OFF");
    }
}

function onMapClick(e) {
    if (!clickToSetMode) return;
    const { lat, lng: lon } = e.latlng;
    const resolved = resolveUserLocation(lat, lon, false);
    resolved.source = "playground";
    if (!resolved.corrected) {
        resolved.lat = lat;
        resolved.lon = lon;
    }
    searchRestSpots(resolved.lat, resolved.lon, "クリック位置（Playground）", resolved);
}

function onFindClick() {
    const btn = document.getElementById("find-btn");
    btn.disabled = true;
    updateStatus("現在地を取得中…");

    const useDefault = () => {
        const resolved = resolveUserLocation(ARIAKE_CENTER.lat, ARIAKE_CENTER.lon, isDemoMode());
        searchRestSpots(resolved.lat, resolved.lon, "有明キャンパス（デフォルト）", resolved);
        btn.disabled = false;
    };

    if (!navigator.geolocation) {
        useDefault();
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const resolved = resolveUserLocation(pos.coords.latitude, pos.coords.longitude);
            const label = resolved.corrected ? "有明キャンパス（エリア外補正）" : "現在地";
            searchRestSpots(resolved.lat, resolved.lon, label, resolved);
            btn.disabled = false;
        },
        () => {
            useDefault();
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
}

async function init() {
    map = L.map("map");
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
        maxZoom: 19,
    }).addTo(map);

    map.setView([DEFAULT_USER.lat, DEFAULT_USER.lon], 14);
    map.on("click", onMapClick);

    let loadError = null;

    try {
        const [scoresRes, restRes] = await Promise.all([
            fetch("data/scores.geojson", { cache: "no-store" }),
            fetch("data/rest_spots.geojson", { cache: "no-store" }),
        ]);

        if (!scoresRes.ok) throw new Error("scores.geojson が見つかりません");
        const scoresGeo = await scoresRes.json();
        gridFeatures = normalizeGridFeatures(scoresGeo.features ?? []);

        if (restRes.ok) {
            const restGeo = await restRes.json();
            restMeta = restGeo.metadata ?? {};
            poiCandidates = restGeo.features ?? [];
        } else {
            loadError = "rest_spots.geojson がありません（デフォルト座標のみ）";
        }
    } catch (e) {
        const msg =
            "データを読み込めません。`python -m heat_town.cli pipeline --sample` を実行してください。";
        updateStatus(msg);
        alert(msg);
        return;
    }

    updateWbgtBanner();

    if (loadError) updateStatus(loadError);
    else updateStatus("準備完了 — ボタンを押して近くの涼み場を探してください");

    document.getElementById("find-btn").addEventListener("click", onFindClick);
    document.getElementById("playground-toggle").addEventListener("click", toggleClickToSetMode);
    document.getElementById("reset-ariake").addEventListener("click", resetToAriake);

    document.getElementById("show-grid").addEventListener("change", renderGrid);

    for (const k of ["w1", "w2", "w3"]) {
        document.getElementById(k).addEventListener("input", () => {
            syncLabels();
            renderGrid();
            document.querySelectorAll(".presets button").forEach((b) => b.classList.remove("active"));
            if (userLocation) {
                searchRestSpots(userLocation.lat, userLocation.lon, "重み変更後");
            }
        });
    }

    document.querySelectorAll(".presets button").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".presets button").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            setWeights(PRESETS[btn.dataset.preset]);
        });
    });

    const initial = resolveUserLocation(ARIAKE_CENTER.lat, ARIAKE_CENTER.lon, isDemoMode());
    searchRestSpots(initial.lat, initial.lon, "有明キャンパス（初期表示）", initial);
}

init();
