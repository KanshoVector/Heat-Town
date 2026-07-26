"""Export decision-model scores as GeoJSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import pandas as pd

from heat_town.model import compute_ji, normalize_weights


def _load_feature_data(data: pd.DataFrame | str | Path) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data

    path = Path(data)
    if path.exists():
        if path.suffix == ".parquet":
            return pd.read_parquet(path)
        if path.suffix == ".csv":
            return pd.read_csv(path)
        if path.suffix in {".json", ".geojson"}:
            return pd.read_json(path)
        raise ValueError(f"Unsupported input format: {path.suffix}")

    return pd.DataFrame(
        [
            {"latitude": 35.1, "longitude": 136.9, "d": 0.2, "C": 70.0, "WBGT": 28.0},
            {"latitude": 35.2, "longitude": 137.0, "d": 0.5, "C": 40.0, "WBGT": 30.0},
            {"latitude": 35.15, "longitude": 136.95, "d": 0.3, "C": 60.0, "WBGT": 31.0},
        ]
    )


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
        Optional 3-tuple of weights ``(w1, w2, w3)``. If omitted, a balanced preset is used.
    """

    data = _load_feature_data(data)

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame or a parquet path")

    if weights is None:
        weights = (0.3, 0.4, 0.3)
    if len(weights) != 3:
        raise ValueError("weights must contain exactly three values")

    w1, w2, w3 = map(float, weights)
    _ = normalize_weights(w1, w2, w3)

    target_path = Path(output_path) if output_path is not None else Path("mvp/public/data/scores.geojson")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    features: list[dict[str, object]] = []
    for _, row in data.iterrows():
        latitude = float(row["latitude"])
        longitude = float(row["longitude"])
        d = float(row["d"])
        comfort = float(row["C"])
        wbgt = float(row["WBGT"])

        ji = compute_ji(d=d, comfort=comfort, wbgt=wbgt, w1=w1, w2=w2, w3=w3)
        distance_contribution = w1 * d
        discomfort_contribution = w2 * (100.0 - comfort)
        heat_contribution = w3 * wbgt

        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "properties": {
                    "ji": ji,
                    "distance_contribution": distance_contribution,
                    "discomfort_contribution": discomfort_contribution,
                    "heat_contribution": heat_contribution,
                    "distance": d,
                    "comfort": comfort,
                    "wbgt": wbgt,
                    "weights": {"w1": w1, "w2": w2, "w3": w3},
                },
            }
        )

    payload = {
        "type": "FeatureCollection",
        "features": features,
    }
    target_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return target_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export decision model scores to GeoJSON")
    parser.add_argument("input_path", nargs="?", default="data/processed/features.parquet")
    parser.add_argument("--output", default="mvp/public/data/scores.geojson")
    parser.add_argument("--weights", nargs=3, type=float, default=[0.3, 0.4, 0.3])
    args = parser.parse_args()

    output_path = export_scores_geojson(args.input_path, output_path=args.output, weights=tuple(args.weights))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
