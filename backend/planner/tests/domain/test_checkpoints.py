from datetime import UTC, datetime, timedelta

import pytest

from planner.domain.checkpoints import place_checkpoints
from planner.domain.types import Piece, Route

MI_M = 1609.344
DEPARTURE = datetime(2026, 11, 16, 14, 0, tzinfo=UTC)


def route_of(*pieces_mi_min: tuple[float, float]) -> Route:
    """A straight eastbound route along the equator, one polyline point per piece boundary.

    Each piece is (miles, minutes). The geometry only matters for coordinate tests,
    which build their own route.
    """
    points = [(float(i), 0.0) for i in range(len(pieces_mi_min) + 1)]
    pieces = [
        Piece(start_index=i, length_m=mi * MI_M, duration_s=minutes * 60)
        for i, (mi, minutes) in enumerate(pieces_mi_min)
    ]
    return Route(points=tuple(points), pieces=tuple(pieces))


def test_checkpoints_every_spacing_plus_the_destination():
    checkpoints = place_checkpoints(route_of((60, 60)), spacing_mi=25, departure=DEPARTURE)

    assert [round(c.mile, 6) for c in checkpoints] == [0, 25, 50, 60]


def test_no_duplicate_destination_when_the_route_ends_on_a_spacing_mile():
    # 500 pieces of 0.1 mi add up to 50.00000000000001 mi in floats, as real HERE data can.
    route = route_of(*[(0.1, 0.1)] * 500)

    checkpoints = place_checkpoints(route, spacing_mi=25, departure=DEPARTURE)

    assert [round(c.mile, 6) for c in checkpoints] == [0, 25, 50]


def test_each_checkpoint_covers_halfway_to_its_neighbours():
    checkpoints = place_checkpoints(route_of((60, 60)), spacing_mi=25, departure=DEPARTURE)

    covers = [(round(c.covers_mi[0], 6), round(c.covers_mi[1], 6)) for c in checkpoints]
    assert covers == [(0, 12.5), (12.5, 37.5), (37.5, 55), (55, 60)]
    assert sum(to - frm for frm, to in covers) == 60


def test_eta_inside_a_piece_is_proportional_to_distance():
    # 60 mi in 90 min: mile 25 is reached after 37.5 min.
    checkpoints = place_checkpoints(route_of((60, 90)), spacing_mi=25, departure=DEPARTURE)

    assert checkpoints[1].eta == DEPARTURE + timedelta(minutes=37.5)
    assert checkpoints[0].eta == DEPARTURE
    assert checkpoints[-1].eta == DEPARTURE + timedelta(minutes=90)


def test_eta_follows_each_piece_speed_not_the_average():
    # 10 mi of city in 20 min, then 50 mi of highway at 60 mph (50 min).
    # Mile 25 = 20 min + 15 highway miles = 35 min. The average speed would give 29 min.
    checkpoints = place_checkpoints(
        route_of((10, 20), (50, 50)), spacing_mi=25, departure=DEPARTURE
    )

    assert [c.eta - DEPARTURE for c in checkpoints] == [
        timedelta(minutes=0),
        timedelta(minutes=35),
        timedelta(minutes=60),
        timedelta(minutes=70),
    ]


def test_coordinates_lie_on_the_line_in_proportion_inside_the_piece():
    # Piece A: points 0 -> 1, 10 mi. Piece B: points 1 -> 3 (two line segments, 1° then 2°), 50 mi.
    route = Route(
        points=((0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (4.0, 0.0)),
        pieces=(
            Piece(start_index=0, length_m=10 * MI_M, duration_s=600),
            Piece(start_index=1, length_m=50 * MI_M, duration_s=3000),
        ),
    )

    checkpoints = place_checkpoints(route, spacing_mi=25, departure=DEPARTURE)

    # Mile 25 is 15 of piece B's 50 mi = 30% of its 3° shape: 0.9° past lon 1.
    # Mile 50 is 80% of 3° = 2.4° past lon 1.
    lons = [c.coordinates[0] for c in checkpoints]
    assert lons == pytest.approx([0.0, 1.9, 3.4, 4.0], abs=1e-6)
    assert all(c.coordinates[1] == pytest.approx(0.0) for c in checkpoints)


def test_a_zero_length_last_piece_still_reaches_the_destination():
    # HERE may end a route with a zero-length span that still has a duration.
    route = Route(
        points=((0.0, 0.0), (1.0, 0.0), (1.0, 0.0)),
        pieces=(
            Piece(start_index=0, length_m=60 * MI_M, duration_s=3600),
            Piece(start_index=1, length_m=0, duration_s=30),
        ),
    )

    checkpoints = place_checkpoints(route, spacing_mi=25, departure=DEPARTURE)

    assert checkpoints[-1].eta == DEPARTURE + timedelta(seconds=3630)
    assert checkpoints[-1].coordinates == pytest.approx((1.0, 0.0))
