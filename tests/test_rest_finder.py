"""Tests for rest spot finder."""

from __future__ import annotations

import pytest

from heat_town.rest_finder import (
    DEFAULT_USER_LAT,
    DEFAULT_USER_LON,
    find_rest_spots,
    google_maps_walking_url,
    haversine_m,
)


def _poi(lat: float, lon: float, kind: str = "park", name: str = "テスト公園") -> dict:
    return {"lat": lat, "lon": lon, "kind": kind, "name": name, "comfort": 90.0}


def test_haversine_zero_distance():
    assert haversine_m(35.634, 139.790, 35.634, 139.790) == pytest.approx(0.0, abs=0.1)


def test_haversine_known_offset():
    # ~111m per 0.001 degree latitude
    dist = haversine_m(35.634, 139.790, 35.635, 139.790)
    assert 100 < dist < 120


def test_find_rest_spots_filters_by_max_walk():
    user_lat, user_lon = DEFAULT_USER_LAT, DEFAULT_USER_LON
    near = _poi(user_lat + 0.001, user_lon, name="近い公園")
    far = _poi(user_lat + 0.05, user_lon, name="遠い公園")
    spots = find_rest_spots(user_lat, user_lon, [near, far], weights=(0.3, 0.4, 0.3), k=3)
    names = [s.name for s in spots]
    assert "近い公園" in names
    assert "遠い公園" not in names


def test_find_rest_spots_top_k_order():
    user_lat, user_lon = DEFAULT_USER_LAT, DEFAULT_USER_LON
    pois = [
        _poi(user_lat + 0.003, user_lon, kind="tree", name="中距離"),
        _poi(user_lat + 0.001, user_lon, kind="park", name="最近"),
        _poi(user_lat + 0.002, user_lon + 0.001, kind="shade_building", name="次点"),
    ]
    spots = find_rest_spots(user_lat, user_lon, pois, weights=(0.3, 0.4, 0.3), k=2)
    assert len(spots) == 2
    assert spots[0].rank == 1
    assert spots[0].score <= spots[1].score
    assert spots[0].name == "最近"


def test_find_rest_spots_maps_url():
    user_lat, user_lon = DEFAULT_USER_LAT, DEFAULT_USER_LON
    poi = _poi(user_lat + 0.001, user_lon)
    spots = find_rest_spots(user_lat, user_lon, [poi], weights=(0.3, 0.4, 0.3))
    assert spots[0].maps_url.startswith("https://www.google.com/maps/dir/")
    assert "travelmode=walking" in spots[0].maps_url


def test_find_rest_spots_geojson_feature_input():
    user_lat, user_lon = DEFAULT_USER_LAT, DEFAULT_USER_LON
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [user_lon + 0.001, user_lat + 0.001]},
        "properties": {"kind": "park", "name": "GeoJSON公園", "comfort": 88},
    }
    spots = find_rest_spots(user_lat, user_lon, [feature], weights=(0.3, 0.4, 0.3))
    assert spots[0].name == "GeoJSON公園"


def test_find_rest_spots_invalid_weights():
    with pytest.raises(ValueError):
        find_rest_spots(0, 0, [], weights=(0.5, 0.5))


def test_google_maps_walking_url_format():
    url = google_maps_walking_url(35.634, 139.790)
    assert "destination=35.634000,139.790000" in url
    assert "travelmode=walking" in url


def test_google_maps_walking_url_with_origin():
    url = google_maps_walking_url(35.635, 139.791, origin_lat=35.634, origin_lon=139.790)
    assert "origin=35.634000,139.790000" in url
    assert "destination=35.635000,139.791000" in url


def test_walk_min_calculation():
    user_lat, user_lon = DEFAULT_USER_LAT, DEFAULT_USER_LON
    # ~111m away
    poi = _poi(user_lat + 0.001, user_lon)
    spots = find_rest_spots(user_lat, user_lon, [poi], weights=(0.3, 0.4, 0.3))
    assert spots[0].walk_min == pytest.approx(spots[0].distance_m / 80.0, rel=0.01)


def test_score_lower_for_closer_poi():
    user_lat, user_lon = DEFAULT_USER_LAT, DEFAULT_USER_LON
    close = _poi(user_lat + 0.001, user_lon, name="A")
    far = _poi(user_lat + 0.004, user_lon, name="B")
    close_spots = find_rest_spots(user_lat, user_lon, [close], weights=(0.3, 0.4, 0.3))
    far_spots = find_rest_spots(user_lat, user_lon, [far], weights=(0.3, 0.4, 0.3))
    assert close_spots[0].score < far_spots[0].score
