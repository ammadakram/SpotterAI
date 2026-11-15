import pytest

from planner.domain.ranking import RankCandidate, rank
from planner.domain.types import RiskLevel, RouteAssessment

L = RiskLevel


def candidate(
    route_id: str,
    *,
    severe: float = 0,
    high: float = 0,
    average: float = 0.5,
    duration_s: float = 40_000,
    drivable: bool = True,
) -> RankCandidate:
    risk_miles = dict.fromkeys(RiskLevel, 0.0) | {L.SEVERE: severe, L.HIGH: high}
    if not drivable:
        risk_miles[L.NO_TRAVEL] = 5.0
    assessment = RouteAssessment(
        risk_miles=risk_miles, average_risk=average, stretches=[], is_drivable=drivable
    )
    return RankCandidate(route_id=route_id, assessment=assessment, duration_s=duration_s)


@pytest.mark.parametrize(
    ("candidates", "order", "decided_by"),
    [
        pytest.param(
            [candidate("r1", severe=20), candidate("r2", severe=10, high=300)],
            ["r2", "r1"],
            "SEVERE_MILES",
            id="fewer severe miles wins even with far more high miles",
        ),
        pytest.param(
            [candidate("r1", severe=10, high=40), candidate("r2", severe=10, high=10, average=3)],
            ["r2", "r1"],
            "HIGH_MILES",
            id="tied on severe: fewer high miles wins",
        ),
        pytest.param(
            [candidate("r1", average=0.4), candidate("r2", average=0.3, duration_s=99_999)],
            ["r2", "r1"],
            "AVERAGE_RISK",
            id="tied on both: lower average wins",
        ),
        pytest.param(
            [candidate("r1", duration_s=45_000), candidate("r2", duration_s=44_000)],
            ["r2", "r1"],
            "DURATION",
            id="tied on all risk: shorter trip wins",
        ),
        pytest.param(
            [candidate("r1"), candidate("r2"), candidate("r3")],
            ["r1", "r2", "r3"],
            "DURATION",
            id="full tie keeps HERE's order",
        ),
        pytest.param(
            [candidate("r1", severe=10.0, high=40), candidate("r2", severe=10.04, high=10)],
            ["r2", "r1"],
            "HIGH_MILES",
            id="differences smaller than the shown 0.1 mi are a tie",
        ),
        pytest.param(
            [
                candidate("r1", severe=0, drivable=False),
                candidate("r2", severe=50),
                candidate("r3", severe=60),
            ],
            ["r2", "r3"],
            "SEVERE_MILES",
            id="a route with no travel is left out, however good otherwise",
        ),
        pytest.param(
            [
                candidate("r1", drivable=False),
                candidate("r2", severe=99),
                candidate("r3", drivable=False),
            ],
            ["r2"],
            "ONLY_DRIVABLE",
            id="only one drivable route",
        ),
        pytest.param(
            [candidate("r1", drivable=False), candidate("r2", drivable=False)],
            [],
            None,
            id="no drivable route: no recommendation",
        ),
    ],
)
def test_ranking(candidates, order, decided_by):
    ranking = rank(candidates)

    assert ranking.ordered_route_ids == order
    assert ranking.recommended_route_id == (order[0] if order else None)
    assert ranking.decided_by == decided_by
