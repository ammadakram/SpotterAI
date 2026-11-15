import httpx
import pytest

from planner.tests.api.conftest import load_fixture

DALLAS = {"label": "Dallas, TX, United States", "lon": -96.8, "lat": 32.78}
DENVER = {"label": "Denver, CO, United States", "lon": -104.99, "lat": 39.74}


def plan_body(**overrides):
    body = {
        "origin": DALLAS,
        "destination": DENVER,
        "departureAt": "2026-11-16T14:00:00Z",
        "loadLb": 32000,
        "spacingMi": 25,
    }
    return {**body, **overrides}


def test_plan_returns_three_routes_with_checkpoints(client, fake_here):
    response = client.post("/api/plans", plan_body(), content_type="application/json")

    assert response.status_code == 200
    plan = response.json()
    assert plan["generatedAt"] == "2026-11-16T12:00:00Z"
    assert [r["id"] for r in plan["routes"]] == ["r1", "r2", "r3"]
    assert [r["label"] for r in plan["routes"]] == ["Route A", "Route B", "Route C"]
    assert [r["distanceMi"] for r in plan["routes"]] == [797.6, 882.3, 786.8]

    first = plan["routes"][0]
    assert first["durationS"] == 44109
    assert first["arrivalAt"] == "2026-11-17T02:15:09Z"  # HERE's own arrival, 19:15:09-07:00
    assert first["geometry"][0] == pytest.approx([-96.7999, 32.7797], abs=1e-4)
    assert len(first["checkpoints"]) == 33  # miles 0, 25, ... 775, then 797.6
    assert first["checkpoints"][1] == {
        "mile": 25.0,
        "coordinates": pytest.approx([-97.1909, 32.8386], abs=1e-4),
        "eta": "2026-11-16T14:31:27Z",
        "coversMi": [12.5, 37.5],
    }
    assert first["checkpoints"][-1]["coversMi"] == [786.3, 797.6]


def test_plan_asks_here_for_a_truck_with_the_loaded_weight(client, fake_here):
    client.post("/api/plans", plan_body(), content_type="application/json")

    (request,) = fake_here.requests
    params = request.url.params
    assert params["transportMode"] == "truck"
    assert params["origin"] == "32.78,-96.8"
    assert params["destination"] == "39.74,-104.99"
    assert params["departureTime"] == "2026-11-16T14:00:00Z"
    assert params["alternatives"] == "2"
    # 32,000 lb load + 35,000 lb tractor-trailer = 67,000 lb = 30,391 kg.
    assert params["vehicle[grossWeight]"] == "30391"


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        pytest.param({"loadLb": 45001}, "loadLb", id="load over 45,000 lb"),
        pytest.param({"loadLb": -1}, "loadLb", id="negative load"),
        pytest.param({"spacingMi": 30}, "spacingMi", id="unsupported spacing"),
        # Now is 12:00; up to 10 minutes late is accepted.
        pytest.param({"departureAt": "2026-11-16T11:49:00Z"}, "departureAt", id="departure past"),
        pytest.param({"departureAt": "2026-11-18T12:01:00Z"}, "departureAt", id="departure > 48 h"),
        pytest.param({"departureAt": "tomorrow"}, "departureAt", id="departure not a time"),
        pytest.param({"origin": {**DALLAS, "lat": 91}}, "origin", id="latitude out of range"),
        pytest.param({"destination": None}, "destination", id="missing destination"),
    ],
)
def test_invalid_input_is_rejected_before_calling_here(client, fake_here, overrides, field):
    response = client.post("/api/plans", plan_body(**overrides), content_type="application/json")

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert list(error["details"]) == [field]
    assert error["message"].startswith(field)
    assert fake_here.requests == []


@pytest.mark.parametrize(
    "departure",
    [
        pytest.param("2026-11-16T11:50:00Z", id="10 minutes late"),
        pytest.param("2026-11-18T12:00:00Z", id="exactly 48 h ahead"),
    ],
)
def test_departure_at_the_edges_of_the_window_is_accepted(client, fake_here, departure):
    response = client.post(
        "/api/plans", plan_body(departureAt=departure), content_type="application/json"
    )

    assert response.status_code == 200


def test_body_that_is_not_json_is_a_validation_error(client, fake_here):
    response = client.post("/api/plans", "{not json", content_type="application/json")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_no_route_is_422_no_route_found(client, fake_here):
    fake_here.responses["router.hereapi.com"] = httpx.Response(
        200, json=load_fixture("here_routes_no_route.json")
    )

    response = client.post("/api/plans", plan_body(), content_type="application/json")

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "NO_ROUTE_FOUND",
            "message": "No truck route found between these places.",
            "details": {},
        }
    }


@pytest.mark.parametrize(
    "here_answer",
    [
        pytest.param(httpx.Response(500, text="oops"), id="HERE server error"),
        pytest.param(httpx.Response(401, json={"error": "Unauthorized"}), id="key rejected"),
        pytest.param(httpx.Response(200, text="<html>"), id="body not JSON"),
        pytest.param(httpx.ReadTimeout("timed out"), id="timeout"),
        pytest.param(httpx.ConnectError("refused"), id="cannot connect"),
    ],
)
def test_here_failure_is_502_routing_unavailable(client, fake_here, here_answer):
    fake_here.responses["router.hereapi.com"] = here_answer

    response = client.post("/api/plans", plan_body(), content_type="application/json")

    assert response.status_code == 502
    error = response.json()["error"]
    assert error["code"] == "ROUTING_UNAVAILABLE"
    assert error["message"] == "Truck routing is unavailable right now."
    assert "test-key" not in response.content.decode()
