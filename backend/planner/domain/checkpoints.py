from bisect import bisect_right
from datetime import datetime, timedelta
from itertools import accumulate

from planner.domain.geometry import METERS_PER_MILE, point_along
from planner.domain.types import Checkpoint, LonLat, Route

# The checkpoint spacings the app offers.
SPACINGS_MI = (10, 25, 50)
# Float sums of piece lengths drift; a spacing mile this close to the end is the end.
SAME_MILE_TOLERANCE = 1e-6


def place_checkpoints(route: Route, spacing_mi: float, departure: datetime) -> list[Checkpoint]:
    """Checkpoints at mile 0, spacing, 2 x spacing, ... plus the destination.

    Miles are measured with HERE's piece lengths, so they agree with the route's distance.
    """
    if spacing_mi <= 0:
        raise ValueError(f"spacing must be positive, got {spacing_mi}")
    # Distance and time at the start of each piece, plus the route end.
    start_m = [0.0, *accumulate(piece.length_m for piece in route.pieces)]
    start_s = [0.0, *accumulate(piece.duration_s for piece in route.pieces)]
    total_mi = start_m[-1] / METERS_PER_MILE

    def locate(mile: float) -> tuple[LonLat, float]:
        """Coordinates and seconds after departure at this mile."""
        distance_m = mile * METERS_PER_MILE
        # The piece containing this distance; the route end belongs to the last piece.
        i = min(bisect_right(start_m, distance_m) - 1, len(route.pieces) - 1)
        piece = route.pieces[i]
        # Only the last piece can be reached with zero length; its end is the destination.
        fraction = (distance_m - start_m[i]) / piece.length_m if piece.length_m > 0 else 1.0
        # A piece's shape runs from its first point to where the next piece starts.
        end_index = route.pieces[i + 1].start_index if i + 1 < len(route.pieces) else None
        shape = route.points[piece.start_index : None if end_index is None else end_index + 1]
        return point_along(shape, fraction), start_s[i] + fraction * piece.duration_s

    miles = []
    mile = 0.0
    while mile < total_mi - SAME_MILE_TOLERANCE:
        miles.append(mile)
        mile += spacing_mi
    miles.append(total_mi)

    # Each checkpoint covers the road halfway to the previous and the next one.
    bounds = [0.0] + [(a + b) / 2 for a, b in zip(miles, miles[1:], strict=False)] + [total_mi]

    def time_at(mile: float) -> datetime:
        return departure + timedelta(seconds=locate(mile)[1])

    checkpoints = []
    for i, m in enumerate(miles):
        coordinates, seconds = locate(m)
        checkpoints.append(
            Checkpoint(
                mile=m,
                coordinates=coordinates,
                eta=departure + timedelta(seconds=seconds),
                covers_mi=(bounds[i], bounds[i + 1]),
                covers_time=(time_at(bounds[i]), time_at(bounds[i + 1])),
            )
        )
    return checkpoints
