"""Sum up one route's checkpoint risks: miles per level, average, stretches."""

from planner.domain.risk import SEVERITY
from planner.domain.types import RatedCheckpoint, RiskLevel, RouteAssessment, Stretch


def assess_route(rated: list[RatedCheckpoint]) -> RouteAssessment:
    risk_miles = dict.fromkeys(RiskLevel, 0.0)
    for item in rated:
        from_mi, to_mi = item.checkpoint.covers_mi
        risk_miles[item.risk.level] += to_mi - from_mi

    # Unknown miles are left out: they say nothing about how risky the road is.
    known_miles = sum(
        miles for level, miles in risk_miles.items() if level != RiskLevel.NO_FORECAST
    )
    if known_miles == 0:
        # Cannot happen: the first checkpoint is at departure, which is inside the forecast.
        raise ValueError("route has no checkpoint with a forecast")
    weighted = sum(
        SEVERITY.index(level) * miles
        for level, miles in risk_miles.items()
        if level != RiskLevel.NO_FORECAST
    )

    return RouteAssessment(
        risk_miles=risk_miles,
        average_risk=weighted / known_miles,
        stretches=_stretches(rated),
        is_drivable=risk_miles[RiskLevel.NO_TRAVEL] == 0,
    )


def _stretches(rated: list[RatedCheckpoint]) -> list[Stretch]:
    stretches: list[Stretch] = []
    for item in rated:
        level = item.risk.level
        (from_mi, to_mi), (starts_at, ends_at) = (
            item.checkpoint.covers_mi,
            item.checkpoint.covers_time,
        )
        if stretches and stretches[-1].level == level:
            last = stretches[-1]
            stretches[-1] = Stretch(level, last.from_mi, to_mi, last.starts_at, ends_at)
        else:
            stretches.append(Stretch(level, from_mi, to_mi, starts_at, ends_at))
    return stretches
