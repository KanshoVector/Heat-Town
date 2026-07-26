"""Tests for demo-safe location resolution and empty-result fallback."""

from __future__ import annotations

import pytest

from heat_town.rest_finder import (
    ARIAKE_CENTER_LAT,
    ARIAKE_CENTER_LON,
    SERVICE_AREA_RADIUS_M,
    find_rest_spots_with_fallback,
    is_in_service_area,
    resolve_user_location,
)

# 越谷市付近（有明から ~30km）— デモエリア外の代表例
YOSHIGAYA_LAT = 35.891
YOSHIGAYA_LON = 139.791


def test_is_in_service_area_at_center():
    assert is_in_service_area(ARIAKE_CENTER_LAT, ARIAKE_CENTER_LON) is True


def test_is_in_service_area_within_radius():
    # ~1km north of center
    assert is_in_service_area(ARIAKE_CENTER_LAT + 0.009, ARIAKE_CENTER_LON) is True


def test_is_in_service_area_outside_radius():
    assert is_in_service_area(YOSHIGAYA_LAT, YOSHIGAYA_LON) is False


def test_resolve_user_location_gps_inside():
    resolved = resolve_user_location(ARIAKE_CENTER_LAT, ARIAKE_CENTER_LON)
    assert resolved.corrected is False
    assert resolved.source == "gps"
    assert resolved.banner_message is None


def test_resolve_user_location_out_of_area():
    resolved = resolve_user_location(YOSHIGAYA_LAT, YOSHIGAYA_LON)
    assert resolved.corrected is True
    assert resolved.source == "out-of-area-fallback"
    assert resolved.lat == pytest.approx(ARIAKE_CENTER_LAT)
    assert resolved.lon == pytest.approx(ARIAKE_CENTER_LON)
    assert resolved.banner_message is not None


def test_resolve_user_location_demo_mode():
    resolved = resolve_user_location(YOSHIGAYA_LAT, YOSHIGAYA_LON, demo_mode=True)
    assert resolved.corrected is True
    assert resolved.source == "demo-forced"
    assert resolved.lat == pytest.approx(ARIAKE_CENTER_LAT)


def test_find_rest_spots_with_fallback_empty_input():
    spots, used = find_rest_spots_with_fallback(
        YOSHIGAYA_LAT,
        YOSHIGAYA_LON,
        poi_data=[],
        weights=(0.3, 0.4, 0.3),
    )
    assert used is True
    assert spots == []


def test_find_rest_spots_with_fallback_out_of_area():
    """越谷から検索しても有明フォールバックで候補が返る（サンプル POI 前提）."""
    from heat_town import samples

    samples.main()
    import json
    from pathlib import Path

    poi_geo = json.loads(
        (Path(samples._samples_dir()) / "poi" / "poi.geojson").read_text()
    )
    pois = poi_geo["features"]

    spots_far, _ = find_rest_spots_with_fallback(
        YOSHIGAYA_LAT, YOSHIGAYA_LON, pois, weights=(0.3, 0.4, 0.3), k=3
    )
    spots_home, _ = find_rest_spots_with_fallback(
        ARIAKE_CENTER_LAT, ARIAKE_CENTER_LON, pois, weights=(0.3, 0.4, 0.3), k=3
    )
    assert len(spots_far) >= 1
    assert len(spots_home) >= 1
    assert spots_far[0].name == spots_home[0].name


def test_service_area_radius_boundary():
    # Just inside 1.5km
    inside = ARIAKE_CENTER_LAT + (SERVICE_AREA_RADIUS_M - 50) / 111_320
    assert is_in_service_area(inside, ARIAKE_CENTER_LON) is True
    # Clearly outside 1.5km (~2km)
    outside = ARIAKE_CENTER_LAT + 2000 / 111_320
    assert is_in_service_area(outside, ARIAKE_CENTER_LON) is False
