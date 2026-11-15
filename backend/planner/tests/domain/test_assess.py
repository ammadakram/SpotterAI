from datetime import UTC, datetime, timedelta

import pytest

from planner.domain.assess import assess_route
from planner.domain.types import Checkpoint, CheckpointRisk, RatedCheckpoint, RiskLevel, Stretch

L = RiskLevel
DEPARTURE = datetime(2026, 11, 16, 14, 0, tzinfo=UTC)


def at_mile(mile: float) -> datetime:
    return DEPARTURE + timedelta(minutes=mile)  # 60 mph keeps the times easy to read


def rated(from_mi: float, to_mi: float, level: RiskLevel) -> RatedCheckpoint:
    checkpoint = Checkpoint(
        mile=(from_mi + to_mi) / 2,
        coordinates=(0.0, 0.0),
        eta=at_mile((from_mi + to_mi) / 2),
        covers_mi=(from_mi, to_mi),
        covers_time=(at_mile(from_mi), at_mile(to_mi)),
    )
    no_forecast = level == L.NO_FORECAST
    risk = CheckpointRisk(
        level=level,
        wind=None if no_forecast else level,
        rain=None if no_forecast else L.LOW,
        snow=None if no_forecast else L.LOW,
        is_load_escalated=False,
        no_forecast_reason="beyond the forecast" if no_forecast else None,
    )
    return RatedCheckpoint(checkpoint=checkpoint, weather=None, risk=risk)


# Checkpoints at miles 0, 25, 50, 60 cover 12.5, 25, 17.5 and 5 miles.
ROUTE = [
    rated(0, 12.5, L.LOW),
    rated(12.5, 37.5, L.HIGH),
    rated(37.5, 55, L.HIGH),
    rated(55, 60, L.NO_FORECAST),
]


def test_miles_per_level_with_unknown_kept_apart():
    assessment = assess_route(ROUTE)

    assert assessment.risk_miles == {
        L.LOW: 12.5,
        L.MODERATE: 0,
        L.HIGH: 42.5,
        L.SEVERE: 0,
        L.NO_TRAVEL: 0,
        L.NO_FORECAST: 5,
    }
    assert sum(assessment.risk_miles.values()) == 60


def test_average_risk_is_weighted_by_miles_and_ignores_unknown_miles():
    # (0 x 12.5 + 2 x 42.5) / 55 known miles
    assert assess_route(ROUTE).average_risk == pytest.approx(85 / 55)


def test_neighbouring_checkpoints_with_the_same_level_form_one_stretch():
    assert assess_route(ROUTE).stretches == [
        Stretch(L.LOW, 0, 12.5, at_mile(0), at_mile(12.5)),
        Stretch(L.HIGH, 12.5, 55, at_mile(12.5), at_mile(55)),
        Stretch(L.NO_FORECAST, 55, 60, at_mile(55), at_mile(60)),
    ]


def test_a_route_with_any_no_travel_is_not_drivable():
    assert assess_route(ROUTE).is_drivable is True
    blocked = [*ROUTE[:2], rated(37.5, 55, L.NO_TRAVEL), ROUTE[3]]
    assert assess_route(blocked).is_drivable is False
