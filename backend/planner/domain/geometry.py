"""Distances and positions on a line of (lon, lat) points."""

from math import asin, cos, radians, sin, sqrt

from planner.domain.types import LonLat

EARTH_RADIUS_M = 6_371_008.8
METERS_PER_MILE = 1609.344


def distance_m(a: LonLat, b: LonLat) -> float:
    """Great-circle (haversine) distance in metres."""
    lon1, lat1, lon2, lat2 = map(radians, (*a, *b))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(sqrt(h))


def point_along(points: tuple[LonLat, ...], fraction: float) -> LonLat:
    """The point `fraction` (0..1) of the way along the line, measured by distance."""
    lengths = [distance_m(a, b) for a, b in zip(points, points[1:], strict=False)]
    remaining = fraction * sum(lengths)
    for (a, b), length in zip(zip(points, points[1:], strict=False), lengths, strict=True):
        if remaining <= length and length > 0:
            t = remaining / length
            return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        remaining -= length
    return points[-1]
