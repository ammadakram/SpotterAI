import json
from pathlib import Path

import pytest

from planner.clients.here import parse_routes
from planner.errors import NoRouteFound, RoutingUnavailable

FIXTURES = Path(__file__).parent.parent / "fixtures"
MI_M = 1609.344
# From the summaries in the fixture (HERE's own totals).
DURATIONS_S = [44109, 45181, 44309]


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_parses_every_route_with_heres_distance_and_duration():
    routes = parse_routes(load_fixture("here_routes_dallas_denver.json"))

    assert [round(r.distance_m / MI_M, 1) for r in routes] == [797.6, 882.3, 786.8]
    assert [r.duration_s for r in routes] == DURATIONS_S


def test_no_route_notice_raises_no_route_found():
    with pytest.raises(NoRouteFound):
        parse_routes(load_fixture("here_routes_no_route.json"))


def _first_section(data: dict) -> dict:
    return data["routes"][0]["sections"][0]


@pytest.mark.parametrize(
    "break_it",
    [
        pytest.param(lambda d: d.pop("routes"), id="no routes key"),
        pytest.param(lambda d: d.update(routes=[]), id="empty routes without a no-route notice"),
        pytest.param(lambda d: _first_section(d).update(polyline="!!"), id="undecodable polyline"),
        pytest.param(lambda d: _first_section(d).update(polyline=""), id="empty polyline"),
        pytest.param(lambda d: _first_section(d).update(polyline="B"), id="truncated polyline"),
        pytest.param(lambda d: _first_section(d).update(spans=[]), id="no spans"),
        pytest.param(
            lambda d: _first_section(d)["spans"][3].pop("length"), id="span without length"
        ),
        pytest.param(
            lambda d: _first_section(d)["spans"][-1].update(offset=10**6),
            id="span offset past the end of the line",
        ),
        pytest.param(
            lambda d: _first_section(d)["spans"][0].update(offset=5),
            id="first span not at the start",
        ),
    ],
)
def test_unreadable_response_raises_routing_unavailable(break_it):
    data = load_fixture("here_routes_dallas_denver.json")
    break_it(data)

    with pytest.raises(RoutingUnavailable):
        parse_routes(data)


def _flag(route: dict, severity: str) -> None:
    route["sections"][0]["notices"] = [
        {
            "title": "Violated vehicle restriction.",
            "code": "violatedVehicleRestriction",
            "severity": severity,
        }
    ]


def test_route_that_breaks_a_truck_restriction_is_dropped():
    data = load_fixture("here_routes_dallas_denver.json")
    _flag(data["routes"][0], "critical")
    _flag(data["routes"][1], "info")  # informational notices don't make a route illegal

    routes = parse_routes(data)

    assert [round(r.distance_m / MI_M, 1) for r in routes] == [882.3, 786.8]


def test_no_route_found_when_every_route_breaks_a_truck_restriction():
    data = load_fixture("here_routes_dallas_denver.json")
    for route in data["routes"]:
        _flag(route, "critical")

    with pytest.raises(NoRouteFound):
        parse_routes(data)
