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


def simplify(points: tuple[LonLat, ...], tolerance_m: float) -> tuple[LonLat, ...]:
    """Douglas–Peucker: drop points that move the drawn line by less than tolerance_m.

    Only for drawing. The ends are always kept. Iterative, so long routes can't hit the
    recursion limit.
    """
    if len(points) <= 2:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        farthest, distance = first, 0.0
        for i in range(first + 1, last):
            d = _distance_to_segment_m(points[i], points[first], points[last])
            if d > distance:
                farthest, distance = i, d
        if distance > tolerance_m:
            keep[farthest] = True
            stack += [(first, farthest), (farthest, last)]
    return tuple(p for p, kept in zip(points, keep, strict=True) if kept)


def _distance_to_segment_m(p: LonLat, a: LonLat, b: LonLat) -> float:
    # Flat-earth metres around the segment: exact enough at the scale of a tolerance.
    m_per_deg_lat = radians(1) * EARTH_RADIUS_M
    m_per_deg_lon = m_per_deg_lat * cos(radians((a[1] + b[1]) / 2))
    px, py = (p[0] - a[0]) * m_per_deg_lon, (p[1] - a[1]) * m_per_deg_lat
    bx, by = (b[0] - a[0]) * m_per_deg_lon, (b[1] - a[1]) * m_per_deg_lat
    length_sq = bx * bx + by * by
    t = 0.0 if length_sq == 0 else max(0.0, min(1.0, (px * bx + py * by) / length_sq))
    return sqrt((px - t * bx) ** 2 + (py - t * by) ** 2)
