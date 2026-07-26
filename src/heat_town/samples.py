"""Generate deterministic sample data into data/samples/.

Usage:
    python -m heat_town.samples
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
CENTER_LAT, CENTER_LON = 35.634, 139.790
SIZE_M, SPACING_M = 2000, 100

# 緯度経度 1 度あたりのメートル（近似）
M_PER_DEG_LAT = 111_320.0
M_PER_DEG_LON = M_PER_DEG_LAT * math.cos(math.radians(CENTER_LAT))


def _samples_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "data" / "samples"


def generate_weather(out_dir: Path) -> Path:
    """真夏日 1 日分の毎時気象データ（Open-Meteo 形式に近い CSV）."""
    rng = np.random.default_rng(SEED)
    hours = pd.date_range("2026-07-25 00:00", periods=24, freq="h")
    # 気温: 深夜 26℃ → 15 時ピーク 35℃ の日変化
    t_peak = 15
    temp = 30.5 + 4.5 * np.cos((hours.hour - t_peak) / 24 * 2 * np.pi) * -1
    temp = 26.0 + (temp - temp.min()) / (temp.max() - temp.min()) * 9.0
    temp += rng.normal(0, 0.3, 24)
    # 湿度: 気温と逆相関（50–85%）
    rh = 85.0 - (temp - temp.min()) / (temp.max() - temp.min()) * 35.0
    rh += rng.normal(0, 2.0, 24)
    wind = np.clip(rng.gamma(2.0, 1.2, 24), 0.2, 8.0)

    df = pd.DataFrame(
        {
            "time": hours,
            "temperature_2m": temp.round(1),
            "relative_humidity_2m": rh.round(1),
            "wind_speed_10m": wind.round(1),
        }
    )
    out = out_dir / "weather" / "weather_hourly.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return out


_KIND_LABELS = {"park": "公園", "tree": "街路樹", "shade_building": "ビル影"}


def generate_poi(out_dir: Path) -> Path:
    """公園・街路樹・建物影の POI（OSM 風 GeoJSON）."""
    rng = np.random.default_rng(SEED)
    kinds = [("park", 6), ("tree", 18), ("shade_building", 8)]
    features = []
    counters: dict[str, int] = {}
    for kind, n in kinds:
        for _ in range(n):
            counters[kind] = counters.get(kind, 0) + 1
            dx, dy = rng.uniform(-SIZE_M / 2, SIZE_M / 2, 2)
            lon = CENTER_LON + dx / M_PER_DEG_LON
            lat = CENTER_LAT + dy / M_PER_DEG_LAT
            label = _KIND_LABELS[kind]
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                    "properties": {
                        "kind": kind,
                        "name": f"{label} {counters[kind]}",
                        "poi_id": f"{kind}_{counters[kind]:02d}",
                    },
                }
            )
    out = out_dir / "poi" / "poi.geojson"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"type": "FeatureCollection", "features": features}
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return out


def generate_grid(out_dir: Path) -> Path:
    """2km 四方・100m 間隔の評価グリッド（約 400 点）."""
    half = SIZE_M / 2
    xs = np.arange(-half + SPACING_M / 2, half, SPACING_M)
    rows = []
    for i, dy in enumerate(xs):
        for j, dx in enumerate(xs):
            rows.append(
                {
                    "grid_id": f"g{i:02d}{j:02d}",
                    "latitude": round(CENTER_LAT + dy / M_PER_DEG_LAT, 6),
                    "longitude": round(CENTER_LON + dx / M_PER_DEG_LON, 6),
                }
            )
    df = pd.DataFrame(rows)
    out = out_dir / "grid" / "grid.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return out


def main() -> None:
    out_dir = _samples_dir()
    for path in (generate_weather(out_dir), generate_poi(out_dir), generate_grid(out_dir)):
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
