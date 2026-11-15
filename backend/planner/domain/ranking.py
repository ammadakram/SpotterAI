"""Order the drivable routes and say which criterion picked the winner."""

from dataclasses import dataclass

from planner.domain.types import RiskLevel, RouteAssessment


@dataclass(frozen=True)
class RankCandidate:
    route_id: str
    assessment: RouteAssessment
    duration_s: float


@dataclass(frozen=True)
class Ranking:
    ordered_route_ids: list[str]  # drivable routes only, safest first
    recommended_route_id: str | None
    decided_by: str | None  # SEVERE_MILES | HIGH_MILES | AVERAGE_RISK | DURATION | ONLY_DRIVABLE


# The brief's order, with each value rounded to what the user is shown, so a difference
# nobody can see never decides. Python's sort is stable: a full tie keeps HERE's order.
CRITERIA = [
    ("SEVERE_MILES", lambda c: round(c.assessment.risk_miles[RiskLevel.SEVERE], 1)),
    ("HIGH_MILES", lambda c: round(c.assessment.risk_miles[RiskLevel.HIGH], 1)),
    ("AVERAGE_RISK", lambda c: round(c.assessment.average_risk, 2)),
    ("DURATION", lambda c: round(c.duration_s)),
]


def rank(candidates: list[RankCandidate]) -> Ranking:
    drivable = [c for c in candidates if c.assessment.is_drivable]
    ordered = sorted(drivable, key=lambda c: tuple(key(c) for _, key in CRITERIA))
    ids = [c.route_id for c in ordered]

    if not ordered:
        return Ranking(ordered_route_ids=[], recommended_route_id=None, decided_by=None)
    if len(ordered) == 1:
        return Ranking(ids, ids[0], "ONLY_DRIVABLE")

    best, runner_up = ordered[0], ordered[1]
    decided_by = next(
        (name for name, key in CRITERIA if key(best) != key(runner_up)),
        "DURATION",  # a full tie: the order HERE returned them in decides
    )
    return Ranking(ids, ids[0], decided_by)
