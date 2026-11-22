"""The heatmap's grid: 0.5° cells along the routes."""

from collections.abc import Sequence
from math import ceil, cos, floor, hypot, radians

from planner.domain.types import LonLat

CELL_DEG = 0.5
# Our choice, not the brief's: wide enough to show weather approaching the route.
CORRIDOR_MI = 30.0
MI_PER_DEG_LAT = 69.0


def corridor_cells(lines: Sequence[Sequence[LonLat]]) -> list[LonLat]:
    """Centres of the cells whose centre is within CORRIDOR_MI of any line.

    Centres sit on fixed lines (x.25, x.75), so a place always maps to the same cell and the
    weather cache keeps working across plans.
    """
    cells: set[LonLat] = set()
    for line in lines:
        for a, b in zip(line, line[1:], strict=False):
            cells.update(_cells_near_segment(a, b))
    return sorted(cells)


def _cells_near_segment(a: LonLat, b: LonLat) -> list[LonLat]:
    # Flat-earth miles around the segment: accurate to well under a mile at 30 mi.
    mi_per_deg_lon = MI_PER_DEG_LAT * cos(radians((a[1] + b[1]) / 2))
    pad_lat = CORRIDOR_MI / MI_PER_DEG_LAT
    pad_lon = CORRIDOR_MI / mi_per_deg_lon

    def to_miles(p: LonLat) -> tuple[float, float]:
        return p[0] * mi_per_deg_lon, p[1] * MI_PER_DEG_LAT

    ax, ay = to_miles(a)
    bx, by = to_miles(b)
    near = []
    for lon in _centres(min(a[0], b[0]) - pad_lon, max(a[0], b[0]) + pad_lon):
        for lat in _centres(min(a[1], b[1]) - pad_lat, max(a[1], b[1]) + pad_lat):
            if _distance_to_segment(to_miles((lon, lat)), (ax, ay), (bx, by)) <= CORRIDOR_MI:
                near.append((lon, lat))
    return near


def _centres(low: float, high: float) -> list[float]:
    """Cell centres (k x 0.5 + 0.25) between low and high."""
    first = ceil((low - CELL_DEG / 2) / CELL_DEG)
    last = floor((high - CELL_DEG / 2) / CELL_DEG)
    return [k * CELL_DEG + CELL_DEG / 2 for k in range(first, last + 1)]


def _distance_to_segment(
    p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]
) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_sq = dx * dx + dy * dy
    t = 0.0 if length_sq == 0 else ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq
    t = max(0.0, min(1.0, t))
    return hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))
