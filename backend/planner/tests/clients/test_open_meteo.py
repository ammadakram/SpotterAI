from datetime import UTC, datetime

import httpx
import pytest
from django.core.cache import cache

from planner.clients.open_meteo import OpenMeteoClient
from planner.errors import WeatherUnavailable
from planner.tests.fakes import FakeOpenMeteo


@pytest.fixture
def fake():
    cache.clear()
    return FakeOpenMeteo()


def client_for(fake: FakeOpenMeteo) -> OpenMeteoClient:
    http = httpx.Client(transport=httpx.MockTransport(fake.handle))
    return OpenMeteoClient(http, base_url="https://api.open-meteo.com", api_key=None, cache=cache)


def test_parses_the_hourly_series(fake):
    (series,) = client_for(fake).get_hourly([(-96.8, 32.8)])

    assert series.start == datetime(2026, 11, 15, 19, 0, tzinfo=UTC)
    assert len(series.wind_mph) == 96
    assert series.gust_mph[:3] == [18.1, 18.1, 13.6]
    assert series.rain_in_hr[:3] == [0.0, 0.0, 0.028]
    assert series.wind_mph[0] == 32.8  # the fake's marker: this place's latitude


def test_asks_for_mph_inches_and_96_hours_in_utc(fake):
    client_for(fake).get_hourly([(-96.8, 32.8)])

    params = fake.requests[0].url.params
    assert params["hourly"] == "wind_speed_10m,wind_gusts_10m,rain,showers,snowfall"
    assert params["wind_speed_unit"] == "mph"
    assert params["precipitation_unit"] == "inch"
    assert params["timezone"] == "GMT"
    assert params["forecast_hours"] == "96"


def test_many_places_are_split_into_requests_of_at_most_100_and_keep_their_order(fake):
    points = [(-100.0, 30.0 + i * 0.1) for i in range(150)]

    results = client_for(fake).get_hourly(points)

    assert sorted(fake.requested_places()) == [50, 100]
    assert [s.wind_mph[0] for s in results] == pytest.approx([lat for _, lat in points])


def test_places_in_the_same_005_degree_square_are_fetched_once(fake):
    # Both round to (-96.80, 32.80).
    results = client_for(fake).get_hourly([(-96.801, 32.799), (-96.79, 32.81)])

    assert fake.requested_places() == [1]
    assert results[0] == results[1]


def test_cached_places_are_not_fetched_again(fake):
    client = client_for(fake)
    client.get_hourly([(-96.8, 32.8), (-97.2, 32.85)])

    client.get_hourly([(-96.8, 32.8), (-104.99, 39.74)])

    assert fake.requested_places() == [2, 1]  # only Denver is new


def test_a_failure_is_not_cached(fake):
    client = client_for(fake)
    fake.failure = httpx.Response(500)
    with pytest.raises(WeatherUnavailable):
        client.get_hourly([(-96.8, 32.8)])

    fake.failure = None
    client.get_hourly([(-96.8, 32.8)])

    assert len(fake.requests) == 2


def test_rate_limit_has_its_own_message(fake):
    fake.failure = httpx.Response(
        429, json={"error": True, "reason": "Minutely API request limit exceeded"}
    )

    with pytest.raises(WeatherUnavailable, match="request limit"):
        client_for(fake).get_hourly([(-96.8, 32.8)])


def _drop_snowfall(place):
    del place["hourly"]["snowfall"]


def _rain_in_mm(place):
    place["hourly_units"]["rain"] = "mm"


def _short_rain(place):
    place["hourly"]["rain"] = place["hourly"]["rain"][:10]


def _skip_an_hour(place):
    place["hourly"]["time"][5] = place["hourly"]["time"][6]


@pytest.mark.parametrize(
    "answer",
    [
        pytest.param(httpx.Response(503), id="server error"),
        pytest.param(httpx.ReadTimeout("slow"), id="timeout"),
        pytest.param(httpx.Response(200, text="<html>"), id="not JSON"),
        pytest.param(httpx.Response(200, json=[]), id="no places in the answer"),
    ],
)
def test_bad_answers_are_weather_unavailable(fake, answer):
    fake.failure = answer

    with pytest.raises(WeatherUnavailable):
        client_for(fake).get_hourly([(-96.8, 32.8), (-97.2, 32.85)])


def _nan_wind(place):
    place["hourly"]["wind_speed_10m"][3] = float("nan")


def _negative_rain(place):
    place["hourly"]["rain"][3] = -0.5


@pytest.mark.parametrize(
    "break_place",
    [
        pytest.param(_nan_wind, id="NaN would compare as Low"),
        pytest.param(_negative_rain, id="negative amount"),
        pytest.param(_drop_snowfall, id="variable missing"),
        pytest.param(_rain_in_mm, id="wrong unit"),
        pytest.param(_short_rain, id="variable shorter than the time list"),
        pytest.param(_skip_an_hour, id="hours not consecutive"),
    ],
)
def test_bad_data_is_weather_unavailable(fake, break_place):
    fake.edit = break_place

    with pytest.raises(WeatherUnavailable):
        client_for(fake).get_hourly([(-96.8, 32.8)])
