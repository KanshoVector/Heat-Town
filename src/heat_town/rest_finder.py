"""Find nearest rest spots (POI) ranked by walk distance and J_i comfort."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from heat_town.model import compute_ji, normalize_weights

# 武蔵野大学 有明キャンパス — pipeline デモ・ geolocation フォールバック共通
DEFAULT_USER_LAT = 35.634
DEFAULT_USER_LON = 139.790
ARIAKE_CENTER_LAT = DEFAULT_USER_LAT
ARIAKE_CENTER_LON = DEFAULT_USER_LON
SERVICE_AREA_RADIUS_M = 1500.0

KIND_LABELS: dict[str, str] = {
    "park": "公園",
    "tree": "街路樹",
    "shade_building": "ビル影",
}

# kind 別の快適度ベース（POI 地点での C 推定）
KIND_COMFORT: dict[str, float] = {
    "park": 92.0,
    "tree": 82.0,
    "shade_building": 76.0,
}

WALK_SPEED_M_PER_MIN = 80.0


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres (WGS84)."""
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(min(a, 1.0)))


def google_maps_walking_url(
    lat: float,
    lon: float,
    origin_lat: float | None = None,
    origin_lon: float | None = None,
) -> str:
    dest = f"destination={lat:.6f},{lon:.6f}"
    if origin_lat is not None and origin_lon is not None:
        origin = f"origin={origin_lat:.6f},{origin_lon:.6f}&"
    else:
        origin = ""
    return f"https://www.google.com/maps/dir/?api=1&{origin}{dest}&travelmode=walking"


def comfort_status(comfort: float) -> str:
    if comfort >= 85:
        return "快適"
    if comfort >= 70:
        return "やや快適"
    if comfort >= 55:
        return "普通"
    return "注意"


def estimate_poi_comfort(kind: str, wind: float = 3.0) -> float:
    """Estimate comfort C at a POI from kind and area wind."""
    base = KIND_COMFORT.get(kind, 70.0)
    wind_bonus = min(wind / 8.0 * 15.0, 15.0)
    return min(base + wind_bonus, 100.0)


def _normalize_poi(poi: Mapping[str, Any], index: int) -> dict[str, Any]:
    """Accept flat dict or GeoJSON-like feature."""
    if "geometry" in poi:
        coords = poi["geometry"]["coordinates"]
        props = poi.get("properties") or {}
        lon, lat = float(coords[0]), float(coords[1])
        kind = str(props.get("kind", "tree"))
        name = props.get("name") or f"{KIND_LABELS.get(kind, '涼み場')}{index + 1}"
        return {"lat": lat, "lon": lon, "kind": kind, "name": name, **props}

    lat = float(poi["lat"])
    lon = float(poi["lon"])
    kind = str(poi.get("kind", "tree"))
    name = poi.get("name") or f"{KIND_LABELS.get(kind, '涼み場')}{index + 1}"
    return {"lat": lat, "lon": lon, "kind": kind, "name": name}


@dataclass(frozen=True)
class ResolvedLocation:
    lat: float
    lon: float
    source: str
    corrected: bool
    banner_message: str | None = None


def is_in_service_area(
    lat: float,
    lon: float,
    center_lat: float = ARIAKE_CENTER_LAT,
    center_lon: float = ARIAKE_CENTER_LON,
    radius_m: float = SERVICE_AREA_RADIUS_M,
) -> bool:
    """Return True when *lat/lon* is within the demo service disc."""
    return haversine_m(lat, lon, center_lat, center_lon) <= radius_m


def resolve_user_location(
    gps_lat: float,
    gps_lon: float,
    demo_mode: bool = False,
    center_lat: float = ARIAKE_CENTER_LAT,
    center_lon: float = ARIAKE_CENTER_LON,
    radius_m: float = SERVICE_AREA_RADIUS_M,
) -> ResolvedLocation:
    """Map raw GPS to an in-area search origin (demo-safe)."""
    banner = "📍 デモ表示: 有明キャンパス（現在地がエリア外のため自動補正中）"
    if demo_mode:
        return ResolvedLocation(
            center_lat,
            center_lon,
            source="demo-forced",
            corrected=True,
            banner_message=banner,
        )
    if not is_in_service_area(gps_lat, gps_lon, center_lat, center_lon, radius_m):
        return ResolvedLocation(
            center_lat,
            center_lon,
            source="out-of-area-fallback",
            corrected=True,
            banner_message=banner,
        )
    return ResolvedLocation(gps_lat, gps_lon, source="gps", corrected=False)


def find_rest_spots_with_fallback(
    user_lat: float,
    user_lon: float,
    poi_data: Sequence[Mapping[str, Any]],
    weights: Sequence[float],
    k: int = 3,
    max_walk_m: float = 800.0,
    wbgt: float = 28.0,
    wind: float = 3.0,
    fallback_lat: float = ARIAKE_CENTER_LAT,
    fallback_lon: float = ARIAKE_CENTER_LON,
) -> tuple[list[RestSpot], bool]:
    """Return Top-k spots; if empty, retry from fallback anchor."""
    spots = find_rest_spots(
        user_lat, user_lon, poi_data, weights, k=k, max_walk_m=max_walk_m, wbgt=wbgt, wind=wind
    )
    if spots:
        return spots, False
    spots = find_rest_spots(
        fallback_lat,
        fallback_lon,
        poi_data,
        weights,
        k=k,
        max_walk_m=max_walk_m,
        wbgt=wbgt,
        wind=wind,
    )
    return spots, True


@dataclass(frozen=True)
class RestSpot:
    rank: int
    name: str
    kind: str
    kind_label: str
    lat: float
    lon: float
    distance_m: float
    walk_min: float
    comfort: float
    comfort_status: str
    ji_score: float
    score: float
    wbgt: float
    maps_url: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def find_rest_spots(
    user_lat: float,
    user_lon: float,
    poi_data: Sequence[Mapping[str, Any]],
    weights: Sequence[float],
    k: int = 3,
    max_walk_m: float = 800.0,
    wbgt: float = 28.0,
    wind: float = 3.0,
) -> list[RestSpot]:
    """Return Top-k rest spots sorted by composite score (lower is better).

    Score = 0.6 * (distance_m / max_walk_m) + 0.4 * (ji_score / 100)
    where ji_score uses ``compute_ji`` with d = distance_m / max_walk_m.
    """
    if len(weights) != 3:
        raise ValueError("weights must contain exactly three values")
    if max_walk_m <= 0:
        raise ValueError("max_walk_m must be positive")
    if k <= 0:
        raise ValueError("k must be positive")

    w1, w2, w3 = normalize_weights(float(weights[0]), float(weights[1]), float(weights[2]))

    candidates: list[RestSpot] = []
    for i, raw in enumerate(poi_data):
        poi = _normalize_poi(raw, i)
        dist_m = haversine_m(user_lat, user_lon, poi["lat"], poi["lon"])
        if dist_m > max_walk_m:
            continue

        comfort = float(poi.get("comfort", estimate_poi_comfort(poi["kind"], wind)))
        d_norm = min(dist_m / max_walk_m, 1.0)
        ji = compute_ji(d_norm, comfort, wbgt, w1, w2, w3)
        composite = 0.6 * d_norm + 0.4 * (ji / 100.0)
        kind = poi["kind"]
        candidates.append(
            RestSpot(
                rank=0,
                name=str(poi["name"]),
                kind=kind,
                kind_label=KIND_LABELS.get(kind, kind),
                lat=poi["lat"],
                lon=poi["lon"],
                distance_m=round(dist_m, 1),
                walk_min=round(dist_m / WALK_SPEED_M_PER_MIN, 1),
                comfort=round(comfort, 1),
                comfort_status=comfort_status(comfort),
                ji_score=round(ji, 2),
                score=round(composite, 4),
                wbgt=wbgt,
                maps_url=google_maps_walking_url(poi["lat"], poi["lon"]),
            )
        )

    candidates.sort(key=lambda s: (s.score, s.distance_m))
    return [
        RestSpot(**{**spot.to_dict(), "rank": rank})
        for rank, spot in enumerate(candidates[:k], start=1)
    ]
