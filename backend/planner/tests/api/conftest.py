from datetime import UTC, datetime

import httpx
import pytest
from django.core.cache import cache

from planner import views
from planner.clients.here import HereClient
from planner.clients.open_meteo import OpenMeteoClient
from planner.tests.fakes import FakeOpenMeteo, load_fixture

# Two hours before the departure the routes fixture was recorded for.
NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)


class FakeHere:
    """Stands in for HERE's servers: answers by host and records every request."""

    def __init__(self):
        self.responses = {
            "router.hereapi.com": httpx.Response(
                200, json=load_fixture("here_routes_dallas_denver.json")
            ),
            "autosuggest.search.hereapi.com": httpx.Response(
                200, json=load_fixture("here_autosuggest_dall.json")
            ),
        }
        self.requests: list[httpx.Request] = []

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        response = self.responses[request.url.host]
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def fake_here(monkeypatch):
    fake = FakeHere()
    http = httpx.Client(transport=httpx.MockTransport(fake.handle))
    monkeypatch.setattr(views, "here_client", lambda: HereClient("test-key", http))
    monkeypatch.setattr(views, "now", lambda: NOW)
    return fake


def set_weather(fake: FakeOpenMeteo, *, wind_mph: float, rain_in_hr: float = 0.0) -> None:
    """Make every hour at every place the same weather."""

    def edit(place: dict) -> None:
        hourly = place["hourly"]
        hours = len(hourly["time"])
        hourly.update(
            wind_speed_10m=[wind_mph] * hours,
            wind_gusts_10m=[wind_mph + 10] * hours,
            rain=[rain_in_hr] * hours,
            showers=[0.0] * hours,
            snowfall=[0.0] * hours,
        )

    fake.edit = edit


@pytest.fixture(autouse=True)
def fake_weather(monkeypatch):
    """Calm weather everywhere unless a test changes it."""
    cache.clear()
    fake = FakeOpenMeteo()
    set_weather(fake, wind_mph=5)
    http = httpx.Client(transport=httpx.MockTransport(fake.handle))
    weather = OpenMeteoClient(
        http, base_url="https://api.open-meteo.com", api_key=None, cache=cache
    )
    monkeypatch.setattr(views, "weather_client", lambda: weather)
    return fake
