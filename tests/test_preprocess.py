"""Preprocess tests."""

from __future__ import annotations

import pandas as pd

from heat_town import samples
from heat_town.preprocess import estimate_wbgt, run_sample


def test_wbgt_in_range():
    w = estimate_wbgt(35.0, 60.0)
    assert 0.0 <= w <= 40.0
    # 高温高湿の方が WBGT は高い
    assert estimate_wbgt(35.0, 80.0) > estimate_wbgt(25.0, 40.0)


def test_run_sample_creates_features():
    samples.main()  # samples を用意
    out = run_sample(hour=15)
    assert out.exists()
    df = pd.read_parquet(out)
    for col in ["grid_id", "latitude", "longitude", "d", "C", "WBGT"]:
        assert col in df.columns
    assert (df["d"].between(0, 1)).all()      # 正規化距離は [0,1]
    assert (df["C"].between(0, 100)).all()    # 快適度は [0,100]
    assert len(df) > 300