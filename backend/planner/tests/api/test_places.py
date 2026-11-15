import httpx

from planner.tests.fakes import load_fixture


def test_places_returns_label_and_coordinates(client, fake_here):
    response = client.get("/api/places", {"q": "dall"})

    assert response.status_code == 200
    assert response.json() == {
        "places": [
            {"label": "Dallas, TX, United States", "lon": -96.7951, "lat": 32.77823},
            {"label": "Dallas, IA, United States", "lon": -94.03976, "lat": 41.68482},
        ]
    }


def test_places_asks_here_for_at_most_five_us_results(client, fake_here):
    client.get("/api/places", {"q": "dall"})

    (request,) = fake_here.requests
    assert request.url.params["q"] == "dall"
    assert request.url.params["in"] == "countryCode:USA"
    assert request.url.params["limit"] == "5"


def test_search_term_suggestions_without_a_position_are_dropped(client, fake_here):
    data = load_fixture("here_autosuggest_dall.json")
    data["items"].insert(0, {"title": "dallas pizza", "resultType": "categoryQuery"})
    fake_here.responses["autosuggest.search.hereapi.com"] = httpx.Response(200, json=data)

    response = client.get("/api/places", {"q": "dall"})

    assert [p["label"] for p in response.json()["places"]] == [
        "Dallas, TX, United States",
        "Dallas, IA, United States",
    ]


def test_blank_query_is_a_validation_error(client, fake_here):
    response = client.get("/api/places", {"q": "  "})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert list(response.json()["error"]["details"]) == ["q"]
    assert fake_here.requests == []


def test_here_failure_is_502(client, fake_here):
    fake_here.responses["autosuggest.search.hereapi.com"] = httpx.Response(503)

    response = client.get("/api/places", {"q": "dall"})

    assert response.status_code == 502
    assert response.json()["error"]["message"] == "Place search is unavailable right now."
