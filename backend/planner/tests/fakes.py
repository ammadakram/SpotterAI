"""Fake upstream servers for tests: they answer from recorded JSON and record requests."""

import copy
import json
from pathlib import Path

import httpx

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict | list:
    return json.loads((FIXTURES / name).read_text())


class FakeOpenMeteo:
    """Answers any forecast request with the recorded data of one real place.

    To let tests check that each result belongs to the right place, every place's
    first wind value is set to its latitude.
    """

    def __init__(self):
        self.template = load_fixture("open_meteo_two_places.json")[0]
        self.requests: list[httpx.Request] = []
        self.failure: httpx.Response | Exception | None = None
        self.edit = lambda place: None  # tests can break the data per place

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if isinstance(self.failure, Exception):
            raise self.failure
        if self.failure is not None:
            return self.failure
        lats = [float(v) for v in request.url.params["latitude"].split(",")]
        lons = [float(v) for v in request.url.params["longitude"].split(",")]
        places = []
        for lat, lon in zip(lats, lons, strict=True):
            place = copy.deepcopy(self.template)
            place.update(latitude=lat, longitude=lon)
            place["hourly"]["wind_speed_10m"][0] = lat
            self.edit(place)
            places.append(place)
        # Open-Meteo answers one place with an object and several with a list.
        # json.dumps (unlike httpx's json=) writes NaN, as a real server might.
        body = json.dumps(places[0] if len(places) == 1 else places)
        return httpx.Response(200, content=body, headers={"content-type": "application/json"})

    def requested_places(self) -> list[int]:
        return [len(r.url.params["latitude"].split(",")) for r in self.requests]
