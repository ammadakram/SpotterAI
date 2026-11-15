import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from planner import views
from planner.clients.here import HereClient

FIXTURES = Path(__file__).parent.parent / "fixtures"
# Two hours before the departure the routes fixture was recorded for.
NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


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
