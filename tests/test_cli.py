"""CLI smoke tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from heat_town import cli, samples


def test_build_grid_creates_points():
    cli.main(["build-grid"])
    grid = samples._samples_dir() / "grid" / "grid.csv"
    assert grid.exists()
    df = pd.read_csv(grid)
    assert len(df) > 300  # 2km / 100m → 約 400 点


def test_fetch_weather_sample():
    cli.main(["fetch-weather", "--sample"])
    weather = samples._samples_dir() / "weather" / "weather_hourly.csv"
    assert weather.exists()
    assert len(pd.read_csv(weather)) == 24


def test_fetch_full_not_implemented():
    with pytest.raises(SystemExit):
        cli.main(["fetch-weather", "--full"])


def test_pipeline_sample_runs():
    cli.main(["pipeline", "--sample"])
    scores = Path(__file__).resolve().parents[1] / "mvp" / "public" / "data" / "scores.geojson"
    assert scores.exists()

