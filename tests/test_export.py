"""Export tests — features.parquet -> scores.geojson の接続確認."""

from __future__ import annotations

import json

import pytest

from heat_town import samples
from heat_town.export import export_scores_geojson
from heat_town.preprocess import run_sample


def test_export_from_features(tmp_path):
    # samples → features.parquet → scores.geojson の一気通し
    samples.main()
    features = run_sample(hour=15)

    out = tmp_path / "scores.geojson"
    result = export_scores_geojson(features, output_path=out)
    assert result.exists()

    geo = json.loads(result.read_text())
    assert geo["type"] == "FeatureCollection"
    assert len(geo["features"]) > 300

    # 各 Feature に寄与3項が入っているか（Explainability の要）
    props = geo["features"][0]["properties"]
    for key in [
        "ji",
        "distance_contribution",
        "discomfort_contribution",
        "heat_contribution",
    ]:
        assert key in props


def test_export_weights_normalized(tmp_path):
    samples.main()
    features = run_sample(hour=15)
    out = tmp_path / "scores.geojson"
    export_scores_geojson(features, output_path=out, weights=(0.6, 0.6, 0.6))
    props = json.loads(out.read_text())["features"][0]["properties"]
    w = props["weights"]
    assert w["w1"] == pytest.approx(w["w2"]) == pytest.approx(w["w3"]) == pytest.approx(1 / 3)


def test_export_weights_length_validation(tmp_path):
    with pytest.raises(ValueError):
        export_scores_geojson(
            samples._samples_dir().parent / "processed" / "features.parquet",
            output_path=tmp_path / "x.geojson",
            weights=(0.5, 0.5),  # 3個でない → エラー
        )
