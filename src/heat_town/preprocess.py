"""Preprocess sample data into a feature table.

Implements feature engineering described in docs/PROJECT.md:
- WBGT estimation from temperature & humidity
- Comfort C from shade / green / wind proxies
- Normalized distance d from an origin point

Usage:
    python -m heat_town.preprocess          # samples -> features.parquet
    from heat_town.preprocess import run_sample
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

M_PER_DEG_LAT = 111_320.0


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_yaml(name: str) -> dict:
    path = _repo_root() / "config" / name
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def estimate_wbgt(temp: float, rh: float) -> float:
    """簡易 WBGT 推定（docs/PROJECT.md と同一式）."""
    wbgt = 0.735 * temp + 0.0375 * rh + 0.00292 * temp * rh + 7.85
    return float(np.clip(wbgt, 0.0, 40.0))


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _nearest_poi_distances(lats: np.ndarray, lons: np.ndarray, pois: list[dict]) -> np.ndarray:
    """各グリッド点から最寄り POI までの距離 (m)。ベクトル化で O(N*M) を定数因子削減."""
    if not pois:
        return np.full(len(lats), 1500.0)

    poi_lats = np.array([p["lat"] for p in pois], dtype=float)
    poi_lons = np.array([p["lon"] for p in pois], dtype=float)

    lat1 = np.radians(lats)[:, None]
    lon1 = np.radians(lons)[:, None]
    lat2 = np.radians(poi_lats)[None, :]
    lon2 = np.radians(poi_lons)[None, :]

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    dists = 2 * 6_371_000.0 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))
    return dists.min(axis=1)


def run_sample(hour: int = 15) -> Path:
    """samples を読み、指定時刻の features.parquet を生成して返す."""
    root = _repo_root()
    samples_dir = root / "data" / "samples"

    origin_cfg = _load_yaml("origin.yaml")["origin"]
    d_max = _load_yaml("origin.yaml")["d_max_m"]
    o_lat, o_lon = origin_cfg["latitude"], origin_cfg["longitude"]

    weather = pd.read_csv(samples_dir / "weather" / "weather_hourly.csv", parse_dates=["time"])
    row = weather.loc[weather["time"].dt.hour == hour]
    if row.empty:
        row = weather.iloc[[hour % len(weather)]]
    temp = float(row["temperature_2m"].iloc[0])
    rh = float(row["relative_humidity_2m"].iloc[0])
    wind = float(row["wind_speed_10m"].iloc[0])
    wbgt = estimate_wbgt(temp, rh)

    poi_geo = json.loads((samples_dir / "poi" / "poi.geojson").read_text())
    pois = [
        {"lat": f["geometry"]["coordinates"][1], "lon": f["geometry"]["coordinates"][0]}
        for f in poi_geo["features"]
    ]

    grid = pd.read_csv(samples_dir / "grid" / "grid.csv")
    lats = grid["latitude"].to_numpy(dtype=float)
    lons = grid["longitude"].to_numpy(dtype=float)

    dist_o = np.array([_haversine_m(lat, lon, o_lat, o_lon) for lat, lon in zip(lats, lons)])
    d = np.clip(dist_o / d_max, 0.0, 1.0)

    poi_dist = _nearest_poi_distances(lats, lons, pois)
    c_green = np.clip(100.0 - poi_dist / 5.0, 0.0, 100.0)
    c_wind = np.clip(wind / 8.0 * 100.0, 0.0, 100.0)
    comfort = np.clip(0.8 * c_green + 0.2 * c_wind, 0.0, 100.0)

    features = pd.DataFrame(
        {
            "grid_id": grid["grid_id"].values,
            "latitude": lats,
            "longitude": lons,
            "d": np.round(d, 4),
            "C": np.round(comfort, 2),
            "WBGT": round(wbgt, 2),
            "hour": hour,
        }
    )

    out = root / "data" / "processed" / "features.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(out, index=False)
    return out


def main() -> None:
    out = run_sample()
    df = pd.read_parquet(out)
    print(f"Wrote {out}  ({len(df)} rows)")
    print(df.head())


if __name__ == "__main__":
    main()
