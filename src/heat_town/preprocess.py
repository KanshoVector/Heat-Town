"""Preprocess sample data into a feature table.

Implements the feature engineering described in docs/data.md:
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
    """簡易 WBGT 推定（docs/data.md の式）.

    WBGT = 0.735*T + 0.0375*RH + 0.00292*T*RH + 7.85 ... ではなく
    docs の係数に合わせた近似。0-40℃ にクリップ。
    """
    wbgt = 0.735 * temp + 0.0375 * rh + 0.00292 * temp * rh - 4.0
    return float(np.clip(wbgt, 0.0, 40.0))


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _nearest_poi_dist(lat: float, lon: float, pois: list[dict]) -> float:
    """最寄り緑・日陰 POI までの距離 (m)。POI 無しは大きめの値。"""
    if not pois:
        return 1500.0
    dists = [_haversine_m(lat, lon, p["lat"], p["lon"]) for p in pois]
    return min(dists)


def run_sample(hour: int = 15) -> Path:
    """samples を読み、指定時刻の features.parquet を生成して返す。"""
    root = _repo_root()
    samples_dir = root / "data" / "samples"

    # --- config ---
    origin_cfg = _load_yaml("origin.yaml")["origin"]
    d_max = _load_yaml("origin.yaml")["d_max_m"]
    o_lat, o_lon = origin_cfg["latitude"], origin_cfg["longitude"]

    # --- weather（指定時刻の1行を使う）---
    weather = pd.read_csv(samples_dir / "weather" / "weather_hourly.csv", parse_dates=["time"])
    row = weather.loc[weather["time"].dt.hour == hour]
    if row.empty:
        row = weather.iloc[[hour % len(weather)]]
    temp = float(row["temperature_2m"].iloc[0])
    rh = float(row["relative_humidity_2m"].iloc[0])
    wind = float(row["wind_speed_10m"].iloc[0])
    wbgt = estimate_wbgt(temp, rh)

    # --- POI ---
    poi_geo = json.loads((samples_dir / "poi" / "poi.geojson").read_text())
    pois = [
        {"lat": f["geometry"]["coordinates"][1], "lon": f["geometry"]["coordinates"][0]}
        for f in poi_geo["features"]
    ]

    # --- grid → 特徴量 ---
    grid = pd.read_csv(samples_dir / "grid" / "grid.csv")
    records = []
    for _, g in grid.iterrows():
        lat, lon = g["latitude"], g["longitude"]

        # 距離 d: origin からの距離を d_max で正規化 [0,1]
        dist_o = _haversine_m(lat, lon, o_lat, o_lon)
        d = min(dist_o / d_max, 1.0)

        # 快適度 C: 最寄り緑・日陰が近いほど高い + 風の寄与（docs の α/β/γ 近似）
        poi_dist = _nearest_poi_dist(lat, lon, pois)
        c_green = max(0.0, 100.0 - poi_dist / 5.0)      # 500m で 0
        c_shade = c_green * 0.8
        c_wind = min(wind / 8.0 * 100.0, 100.0)
        comfort = float(np.clip(0.4 * c_shade + 0.4 * c_green + 0.2 * c_wind, 0.0, 100.0))

        records.append(
            {
                "grid_id": g["grid_id"],
                "latitude": lat,
                "longitude": lon,
                "d": round(d, 4),
                "C": round(comfort, 2),
                "WBGT": round(wbgt, 2),
                "hour": hour,
            }
        )

    features = pd.DataFrame.from_records(records)
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