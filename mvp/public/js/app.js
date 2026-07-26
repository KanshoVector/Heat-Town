const PRESETS = {
  balanced: { label: 'balanced', w1: 0.3, w2: 0.4, w3: 0.3 },
  elderly: { label: 'elderly', w1: 0.2, w2: 0.5, w3: 0.3 },
  commuter: { label: 'commuter', w1: 0.5, w2: 0.2, w3: 0.3 },
  heat_alert: { label: 'heat_alert', w1: 0.2, w2: 0.2, w3: 0.6 },
};

const COLORS = ['#2ecc71', '#8bd34a', '#f1c40f', '#e67e22', '#e74c3c'];

const state = {
  weights: { ...PRESETS.balanced },
  features: [],
  map: null,
  layer: null,
};

const elements = {
  status: document.getElementById('status'),
  presetGrid: document.getElementById('preset-grid'),
  sliders: document.getElementById('sliders'),
  legend: document.getElementById('legend'),
};

function format(value, digits = 1) {
  return Number(value).toFixed(digits);
}

function clampWeight(value) {
  return Math.max(0, Number(value) || 0);
}

function normalizeWeights(weights) {
  const total = weights.w1 + weights.w2 + weights.w3;
  if (total <= 0) {
    return { ...PRESETS.balanced };
  }

  return {
    w1: weights.w1 / total,
    w2: weights.w2 / total,
    w3: weights.w3 / total,
    label: weights.label ?? 'custom',
  };
}

function computeJ(feature, weights) {
  const { d, comfort, wbgt } = feature.properties;
  return weights.w1 * d + weights.w2 * (100 - comfort) + weights.w3 * wbgt;
}

function computeContributions(feature, weights) {
  const { d, comfort, wbgt } = feature.properties;
  return {
    distance: weights.w1 * d,
    discomfort: weights.w2 * (100 - comfort),
    heat: weights.w3 * wbgt,
  };
}

function quantile(sortedValues, fraction) {
  if (sortedValues.length === 0) {
    return 0;
  }

  if (sortedValues.length === 1) {
    return sortedValues[0];
  }

  const index = (sortedValues.length - 1) * fraction;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) {
    return sortedValues[lower];
  }

  return sortedValues[lower] + (sortedValues[upper] - sortedValues[lower]) * (index - lower);
}

function getColor(value, breaks) {
  if (value <= breaks[0]) return COLORS[0];
  if (value <= breaks[1]) return COLORS[1];
  if (value <= breaks[2]) return COLORS[2];
  if (value <= breaks[3]) return COLORS[3];
  return COLORS[4];
}

function buildLegend(breaks) {
  const labels = [
    `最良 0–20% <= ${format(breaks[0])}`,
    `${format(breaks[0])}–${format(breaks[1])}`,
    `${format(breaks[1])}–${format(breaks[2])}`,
    `${format(breaks[2])}–${format(breaks[3])}`,
    `高リスク >= ${format(breaks[3])}`,
  ];

  elements.legend.innerHTML = labels
    .map(
      (label, index) => `
        <div class="legend-item">
          <span class="swatch" style="background:${COLORS[index]}"></span>
          <span>${label}</span>
          <span>J_i</span>
        </div>`,
    )
    .join('');
}

function buildPopup(feature) {
  const { name, district } = feature.properties;
  const contributions = feature._contributions;

  return `
    <div>
      <h3 class="popup-title">${name}${district ? ` <small>(${district})</small>` : ''}</h3>
      <div class="popup-score">Ji = ${format(feature._score)}</div>
      <div class="popup-lines">
        <span><strong>距離寄与</strong><em>${format(contributions.distance)}</em></span>
        <span><strong>不快寄与</strong><em>${format(contributions.discomfort)}</em></span>
        <span><strong>暑さ寄与</strong><em>${format(contributions.heat)}</em></span>
      </div>
    </div>`;
}

function updateStatus(message) {
  elements.status.textContent = message;
}

function createSliders() {
  const fields = [
    { key: 'w1', label: '距離', color: '#60a5fa' },
    { key: 'w2', label: '不快', color: '#f59e0b' },
    { key: 'w3', label: '暑さ', color: '#f43f5e' },
  ];

  elements.sliders.innerHTML = fields
    .map(
      ({ key, label, color }) => `
        <div class="slider">
          <label for="${key}">
            <span>${label}</span>
            <output id="${key}-value">${format(state.weights[key])}</output>
          </label>
          <input id="${key}" type="range" min="0" max="100" step="1" value="${Math.round(
            state.weights[key] * 100,
          )}" style="accent-color:${color}" />
        </div>`,
    )
    .join('');

  fields.forEach(({ key }) => {
    const input = document.getElementById(key);
    input.addEventListener('input', () => {
      const updated = {
        ...state.weights,
        label: 'custom',
        [key]: clampWeight(Number(input.value) / 100),
      };

      state.weights = normalizeWeights(updated);
      syncSliderOutputs();
      renderAll();
      setActivePreset('custom');
    });
  });
}

function syncSliderOutputs() {
  ['w1', 'w2', 'w3'].forEach((key) => {
    const input = document.getElementById(key);
    const output = document.getElementById(`${key}-value`);
    if (input) {
      input.value = String(Math.round(state.weights[key] * 100));
    }
    if (output) {
      output.textContent = format(state.weights[key]);
    }
  });
}

function setActivePreset(label) {
  document.querySelectorAll('[data-preset]').forEach((button) => {
    button.classList.toggle('active', button.dataset.preset === label);
  });
}

function createPresets() {
  elements.presetGrid.innerHTML = Object.values(PRESETS)
    .map(
      (preset) => `
        <button type="button" data-preset="${preset.label}">${preset.label}</button>`,
    )
    .join('') + '<button type="button" data-preset="custom">custom</button>';

  elements.presetGrid.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => {
      const preset = PRESETS[button.dataset.preset];
      if (preset) {
        state.weights = { ...preset };
      } else {
        state.weights = normalizeWeights(state.weights);
        state.weights.label = 'custom';
      }

      syncSliderOutputs();
      renderAll();
      setActivePreset(button.dataset.preset);
    });
  });

  setActivePreset(state.weights.label);
}

function normalizeFeatures(features) {
  return features.map((feature, index) => {
    const properties = feature.properties ?? {};
    const d = Number(properties.d ?? properties.distance ?? properties.distance_norm ?? 0);
    const comfort = Number(properties.comfort ?? properties.C ?? 0);
    const wbgt = Number(properties.wbgt ?? properties.WBGT ?? 0);

    return {
      ...feature,
      properties: {
        ...properties,
        name: properties.name ?? `地点 ${index + 1}`,
        district: properties.district ?? '',
        d,
        comfort,
        wbgt,
      },
    };
  });
}

function renderAll() {
  if (!state.features.length) {
    return;
  }

  const normalizedWeights = normalizeWeights(state.weights);
  const scored = state.features.map((feature) => {
    const score = computeJ(feature, normalizedWeights);
    const contributions = computeContributions(feature, normalizedWeights);
    return {
      ...feature,
      _score: score,
      _contributions: contributions,
    };
  });

  const sortedScores = scored.map((feature) => feature._score).sort((a, b) => a - b);
  const breaks = [0.2, 0.4, 0.6, 0.8].map((fraction) => quantile(sortedScores, fraction));

  if (state.layer) {
    state.layer.clearLayers();
    scored.forEach((feature) => {
      const marker = L.circleMarker([feature.geometry.coordinates[1], feature.geometry.coordinates[0]], {
        radius: 6,
        weight: 1.5,
        color: 'rgba(255,255,255,0.85)',
        fillColor: getColor(feature._score, breaks),
        fillOpacity: 0.82,
      });

      marker.bindPopup(buildPopup(feature), { maxWidth: 320 });
      marker.addTo(state.layer);
    });
  }

  buildLegend(breaks);
  updateStatus(`読み込み完了: ${scored.length} 点 | w1=${format(normalizedWeights.w1)} / w2=${format(normalizedWeights.w2)} / w3=${format(normalizedWeights.w3)}`);
}

async function loadData() {
  const response = await fetch('data/scores.geojson', { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`scores.geojson の取得に失敗しました: ${response.status}`);
  }

  const geojson = await response.json();
  const features = Array.isArray(geojson.features) ? geojson.features : [];
  state.features = normalizeFeatures(features);
}

function initMap() {
  state.map = L.map('map', { zoomControl: true });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(state.map);

  state.layer = L.layerGroup().addTo(state.map);
}

function fitMap() {
  if (!state.features.length) {
    return;
  }

  const bounds = L.latLngBounds(state.features.map((feature) => [feature.geometry.coordinates[1], feature.geometry.coordinates[0]]));
  state.map.fitBounds(bounds.pad(0.08), { maxZoom: 16 });
}

async function bootstrap() {
  initMap();
  createPresets();
  createSliders();

  try {
    await loadData();
    renderAll();
    fitMap();
  } catch (error) {
    updateStatus(error instanceof Error ? error.message : 'GeoJSON の読み込みに失敗しました');
    elements.legend.innerHTML = '';
  }
}

window.addEventListener('DOMContentLoaded', bootstrap);