import httpx
import pytest

from planner.clients import open_meteo
from planner.tests.api.conftest import set_weather
from planner.tests.fakes import load_fixture

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
        "risk": "LOW",
        "isLoadEscalated": False,
        "conditions": {"wind": "LOW", "rain": "LOW", "snow": "LOW"},
        "weather": {"windMph": 5.0, "gustMph": 15.0, "rainInHr": 0.0, "snowInHr": 0.0},
        "noForecastReason": None,
    }
    assert first["checkpoints"][-1]["coversMi"] == [786.3, 797.6]


def test_calm_weather_everywhere_recommends_the_quickest_route(client, fake_here):
    plan = client.post("/api/plans", plan_body(), content_type="application/json").json()

    first = plan["routes"][0]
    assert first["isDrivable"] is True
    assert first["riskMiles"] == {
        "low": 797.6,
        "moderate": 0,
        "high": 0,
        "severe": 0,
        "noTravel": 0,
        "unknown": 0,
    }
    assert first["averageRisk"] == 0
    assert first["stretches"] == [
        {
            "level": "LOW",
            "fromMi": 0,
            "toMi": 797.6,
            "startsAt": "2026-11-16T14:00:00Z",
            "endsAt": "2026-11-17T02:15:09Z",
        }
    ]
    # Durations: r1 44,109 s, r3 44,309 s, r2 45,181 s.
    assert plan["ranking"] == {
        "orderedRouteIds": ["r1", "r3", "r2"],
        "recommendedRouteId": "r1",
        "decidedBy": "DURATION",
    }


def test_heavy_load_in_high_wind_makes_every_mile_severe(client, fake_here, fake_weather):
    set_weather(fake_weather, wind_mph=40)

    plan = client.post(
        "/api/plans", plan_body(loadLb=45000), content_type="application/json"
    ).json()

    checkpoint = plan["routes"][0]["checkpoints"][3]
    assert checkpoint["risk"] == "SEVERE"
    assert checkpoint["isLoadEscalated"] is True
    assert [r["riskMiles"]["severe"] for r in plan["routes"]] == [797.6, 882.3, 786.8]
    # Fewest severe miles: the shortest route, r3.
    assert plan["ranking"]["orderedRouteIds"] == ["r3", "r1", "r2"]
    assert plan["ranking"]["decidedBy"] == "SEVERE_MILES"


def test_no_drivable_route_is_still_a_normal_answer(client, fake_here, fake_weather):
    set_weather(fake_weather, wind_mph=50)  # Severe wind + 32,000 lb (> 30,000) = No Travel

    response = client.post("/api/plans", plan_body(), content_type="application/json")

    assert response.status_code == 200
    plan = response.json()
    assert [r["isDrivable"] for r in plan["routes"]] == [False, False, False]
    assert plan["ranking"] == {"orderedRouteIds": [], "recommendedRouteId": None, "decidedBy": None}


def test_weather_failure_is_502_weather_unavailable(client, fake_here, fake_weather):
    fake_weather.failure = httpx.Response(503)

    response = client.post("/api/plans", plan_body(), content_type="application/json")

    assert response.status_code == 502
    assert response.json()["error"] == {
        "code": "WEATHER_UNAVAILABLE",
        "message": "Weather data is unavailable right now.",
        "details": {},
    }


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


def test_weather_without_any_usable_value_is_502_not_a_crash(client, fake_here, fake_weather):
    def no_snow(place):
        place["hourly"]["snowfall"] = [None] * len(place["hourly"]["time"])

    fake_weather.edit = no_snow

    response = client.post("/api/plans", plan_body(), content_type="application/json")

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "WEATHER_UNAVAILABLE"


def test_plan_includes_the_corridor_heatmap(client, fake_here):
    heatmap = client.post("/api/plans", plan_body(), content_type="application/json").json()[
        "heatmap"
    ]

    assert heatmap["startsAt"] == "2026-11-16T12:00:00Z"  # now is exactly 12:00
    assert heatmap["hours"] == 49
    assert heatmap["cellSizeDeg"] == 0.5
    assert len(heatmap["cells"]) > 50  # a corridor along ~800 mi routes
    for cell in heatmap["cells"]:
        lon, lat = cell["center"]
        assert (lon - 0.25) % 0.5 == 0 and (lat - 0.25) % 0.5 == 0
        assert cell["risk"] == [0] * 49  # calm weather: Low everywhere
        assert cell["windMph"] == [5.0] * 49
        assert len(cell["rainInHr"]) == len(cell["snowInHr"]) == 49


def test_heatmap_risk_uses_the_load(client, fake_here, fake_weather):
    set_weather(fake_weather, wind_mph=40)

    heatmap = client.post(
        "/api/plans", plan_body(loadLb=45000), content_type="application/json"
    ).json()["heatmap"]

    assert {r for cell in heatmap["cells"] for r in cell["risk"]} == {3}  # Severe


def test_checkpoints_and_grid_are_fetched_in_one_pass_without_repeats(
    client, fake_here, fake_weather
):
    client.post("/api/plans", plan_body(), content_type="application/json")

    places = [
        (lon, lat)
        for request in fake_weather.requests
        for lon, lat in zip(
            request.url.params["longitude"].split(","),
            request.url.params["latitude"].split(","),
            strict=True,
        )
    ]
    assert len(places) == len(set(places))
    assert all(n <= 100 for n in fake_weather.requested_places())


def test_trip_too_large_for_the_free_weather_plan_is_422_without_any_weather_call(
    client, fake_here, fake_weather, monkeypatch
):
    monkeypatch.setattr(open_meteo, "FREE_PLAN_MAX_NEW_PLACES", 50)

    response = client.post("/api/plans", plan_body(), content_type="application/json")

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "TRIP_TOO_LARGE"
    assert error["message"].endswith("Choose a larger checkpoint spacing.")
    assert error["details"]["limit"] == 50
    assert fake_weather.requests == []


def test_too_large_at_the_widest_spacing_does_not_suggest_a_spacing(
    client, fake_here, fake_weather, monkeypatch
):
    monkeypatch.setattr(open_meteo, "FREE_PLAN_MAX_NEW_PLACES", 50)

    response = client.post("/api/plans", plan_body(spacingMi=50), content_type="application/json")

    assert response.status_code == 422
    message = response.json()["error"]["message"]
    assert "too long for the free weather service" in message
    assert "spacing" not in message


def test_heatmap_values_just_under_a_band_edge_stay_under_it(client, fake_here, fake_weather):
    # Rounding 24.96 up to 25.0 would paint the Wind view Moderate while risk says Low.
    set_weather(fake_weather, wind_mph=24.96, rain_in_hr=0.0999)

    cell = client.post("/api/plans", plan_body(), content_type="application/json").json()[
        "heatmap"
    ]["cells"][0]

    assert cell["risk"][0] == 0
    assert cell["windMph"][0] == 24.9
    assert cell["rainInHr"][0] == 0.099


def test_route_lines_are_simplified_for_drawing_but_keep_their_ends(client, fake_here):
    plan = client.post("/api/plans", plan_body(), content_type="application/json").json()

    first = plan["routes"][0]
    assert len(first["geometry"]) < 8791 / 4  # HERE's line has 8,791 points
    assert first["geometry"][0] == pytest.approx([-96.7999, 32.7797], abs=1e-4)
    assert first["geometry"][-1] == pytest.approx([-104.99, 39.74], abs=1e-4)
    # Distances still come from the full line: HERE's 797.6 mi, not the simplified shape.
    assert first["distanceMi"] == 797.6


@pytest.mark.parametrize(
    "destination",
    [
        pytest.param(DALLAS, id="identical"),
        pytest.param({**DALLAS, "lon": DALLAS["lon"] + 0.0005}, id="a few metres apart"),
    ],
)
def test_origin_and_destination_at_the_same_place_is_rejected(client, fake_here, destination):
    response = client.post(
        "/api/plans", plan_body(destination=destination), content_type="application/json"
    )

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["message"] == "destination: Origin and destination are the same place."
    assert fake_here.requests == []
