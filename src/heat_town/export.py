"""Export decision-model scores as GeoJSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import pandas as pd

from heat_town.model import normalize_weights
from heat_town.rest_finder import (
    ARIAKE_CENTER_LAT,
    ARIAKE_CENTER_LON,
    DEFAULT_USER_LAT,
    DEFAULT_USER_LON,
    KIND_LABELS,
    SERVICE_AREA_RADIUS_M,
    RestSpot,
    estimate_poi_comfort,
    find_rest_spots,
)


def _load_feature_data(data: pd.DataFrame | str | Path) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data

    path = Path(data)
    if not path.exists():
        raise FileNotFoundError(f"Feature file not found: {path}")

    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix in {".json", ".geojson"}:
        return pd.read_json(path)
    raise ValueError(f"Unsupported input format: {path.suffix}")


def export_scores_geojson(
    data: pd.DataFrame | str | Path,
    output_path: str | Path | None = None,
    weights: Sequence[float] | None = None,
) -> Path:
    """Export point-level model scores to a GeoJSON FeatureCollection.

    Parameters
    ----------
    data:
        Either a pandas DataFrame with columns ``latitude``, ``longitude``, ``d``,
        ``C`` and ``WBGT`` or a parquet path pointing to such a table.
    output_path:
        Destination GeoJSON file. Defaults to ``mvp/public/data/scores.geojson``.
    weights:
        Optional 3-tuple of weights ``(w1, w2, w3)``. Normalized to sum 1 before export.
    """

    frame = _load_feature_data(data)

    if weights is None:
        weights = (0.3, 0.4, 0.3)
    if len(weights) != 3:
        raise ValueError("weights must contain exactly three values")

    w1, w2, w3 = normalize_weights(float(weights[0]), float(weights[1]), float(weights[2]))

    target_path = (
        Path(output_path) if output_path is not None else Path("mvp/public/data/scores.geojson")
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)

    required = {"latitude", "longitude", "d", "C", "WBGT"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    lat = frame["latitude"].astype(float)
    lon = frame["longitude"].astype(float)
    d = frame["d"].astype(float)
    comfort = frame["C"].astype(float)
    wbgt = frame["WBGT"].astype(float)

    distance_contribution = w1 * d
    discomfort_contribution = w2 * (100.0 - comfort)
    heat_contribution = w3 * wbgt
    ji = distance_contribution + discomfort_contribution + heat_contribution

    features: list[dict[str, object]] = []
    weight_props = {"w1": w1, "w2": w2, "w3": w3}
    for i in range(len(frame)):
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(lon.iloc[i]), float(lat.iloc[i])],
                },
                "properties": {
                    "ji": float(ji.iloc[i]),
                    "distance_contribution": float(distance_contribution.iloc[i]),
                    "discomfort_contribution": float(discomfort_contribution.iloc[i]),
                    "heat_contribution": float(heat_contribution.iloc[i]),
                    "distance": float(d.iloc[i]),
                    "comfort": float(comfort.iloc[i]),
                    "wbgt": float(wbgt.iloc[i]),
                    "weights": weight_props,
                },
            }
        )

    payload = {
        "type": "FeatureCollection",
        "features": features,
    }
    target_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return target_path


def export_rest_spots_geojson(
    poi_path: str | Path,
    output_path: str | Path | None = None,
    user_lat: float = DEFAULT_USER_LAT,
    user_lon: float = DEFAULT_USER_LON,
    weights: Sequence[float] | None = None,
    k: int = 3,
    max_walk_m: float = 800.0,
    wbgt: float | None = None,
    wind: float = 3.0,
) -> Path:
    """Export Top-k rest spots and all POI candidates for client-side re-ranking."""
    poi_file = Path(poi_path)
    if not poi_file.exists():
        raise FileNotFoundError(f"POI file not found: {poi_file}")

    if weights is None:
        weights = (0.3, 0.4, 0.3)

    poi_geo = json.loads(poi_file.read_text())
    poi_features = poi_geo.get("features", [])

    area_wbgt = wbgt if wbgt is not None else 28.0

    enriched: list[dict[str, object]] = []
    for feature in poi_features:
        props = feature.get("properties") or {}
        kind = str(props.get("kind", "tree"))
        comfort = estimate_poi_comfort(kind, wind)
        enriched.append(
            {
                **feature,
                "properties": {
                    **props,
                    "comfort": comfort,
                    "kind_label": KIND_LABELS.get(kind, kind),
                },
            }
        )

    top_spots = find_rest_spots(
        user_lat,
        user_lon,
        enriched,
        weights=weights,
        k=k,
        max_walk_m=max_walk_m,
        wbgt=area_wbgt,
        wind=wind,
    )
    top_keys = {(s.lat, s.lon) for s in top_spots}

    w1, w2, w3 = normalize_weights(float(weights[0]), float(weights[1]), float(weights[2]))
    w_props = {"w1": w1, "w2": w2, "w3": w3}

    def _spot_props(spot: RestSpot) -> dict[str, object]:
        return {
            "rank": spot.rank,
            "name": spot.name,
            "kind": spot.kind,
            "kind_label": spot.kind_label,
            "distance_m": spot.distance_m,
            "walk_min": spot.walk_min,
            "comfort": spot.comfort,
            "comfort_status": spot.comfort_status,
            "ji_score": spot.ji_score,
            "score": spot.score,
            "wbgt": spot.wbgt,
            "maps_url": spot.maps_url,
            "is_top_k": True,
        }

    features: list[dict[str, object]] = []
    for spot in top_spots:
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [spot.lon, spot.lat]},
                "properties": _spot_props(spot),
            }
        )

    for feature in enriched:
        coords = feature["geometry"]["coordinates"]
        lat, lon = float(coords[1]), float(coords[0])
        if (lat, lon) in top_keys:
            continue
        props = feature["properties"]
        features.append(
            {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": {
                    **props,
                    "rank": None,
                    "is_top_k": False,
                    "wbgt": area_wbgt,
                },
            }
        )

    target_path = (
        Path(output_path)
        if output_path is not None
        else Path("mvp/public/data/rest_spots.geojson")
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "type": "FeatureCollection",
        "metadata": {
            "default_user": {"latitude": user_lat, "longitude": user_lon},
            "service_area": {
                "center": {"latitude": ARIAKE_CENTER_LAT, "longitude": ARIAKE_CENTER_LON},
                "radius_m": SERVICE_AREA_RADIUS_M,
            },
            "weights": w_props,
            "max_walk_m": max_walk_m,
            "wbgt": area_wbgt,
            "wind": wind,
            "walk_speed_m_per_min": 80.0,
            "top_k": k,
        },
        "features": features,
    }
    target_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return target_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export decision model scores to GeoJSON")
    parser.add_argument("input_path", nargs="?", default="data/processed/features.parquet")
    parser.add_argument("--output", default="mvp/public/data/scores.geojson")
    parser.add_argument("--weights", nargs=3, type=float, default=[0.3, 0.4, 0.3])
    parser.add_argument(
        "--rest-spots",
        action="store_true",
        help="Also export rest_spots.geojson from sample POI",
    )
    args = parser.parse_args()

    output_path = export_scores_geojson(
        args.input_path,
        output_path=args.output,
        weights=tuple(args.weights),
    )
    print(f"Wrote {output_path}")

    if args.rest_spots:
        frame = _load_feature_data(args.input_path)
        wbgt = float(frame["WBGT"].iloc[0]) if len(frame) else 28.0
        rest_path = export_rest_spots_geojson(
            "data/samples/poi/poi.geojson",
            weights=tuple(args.weights),
            wbgt=wbgt,
        )
        print(f"Wrote {rest_path}")


if __name__ == "__main__":
    main()
