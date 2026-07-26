"""Export decision-model scores as GeoJSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import pandas as pd

from heat_town.model import normalize_weights


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Export decision model scores to GeoJSON")
    parser.add_argument("input_path", nargs="?", default="data/processed/features.parquet")
    parser.add_argument("--output", default="mvp/public/data/scores.geojson")
    parser.add_argument("--weights", nargs=3, type=float, default=[0.3, 0.4, 0.3])
    args = parser.parse_args()

    output_path = export_scores_geojson(
        args.input_path,
        output_path=args.output,
        weights=tuple(args.weights),
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
