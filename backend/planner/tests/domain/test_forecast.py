from datetime import UTC, datetime, timedelta

import pytest

from planner.domain.forecast import weather_at
from planner.domain.types import HourlySeries, NoForecast, Weather

START = datetime(2026, 11, 16, 9, 0, tzinfo=UTC)  # the first forecast hour


def series(hours: int = 4, **overrides) -> HourlySeries:
    """Hour i has wind 10 + i, so each test can see which hour was picked."""
    values = {
        "wind_mph": [10.0 + i for i in range(hours)],
        "gust_mph": [20.0 + i for i in range(hours)],
        "rain_in_hr": [0.01 * i for i in range(hours)],
        "showers_in_hr": [0.0] * hours,
        "snow_in_hr": [0.0] * hours,
    }
    return HourlySeries(start=START, **{**values, **overrides})


@pytest.mark.parametrize(
    ("eta", "picked_hour"),
    [
        pytest.param(
            START + timedelta(minutes=45),
            1,
            id="9:45 uses 10:00 (rain is for the hour ending 10:00)",
        ),
        pytest.param(START + timedelta(hours=1), 1, id="exactly 10:00 uses 10:00"),
        pytest.param(START + timedelta(hours=1, seconds=1), 2, id="10:00:01 uses 11:00"),
        pytest.param(START, 0, id="the first hour itself"),
    ],
)
def test_picks_the_hour_the_truck_is_driving_in(eta, picked_hour):
    weather = weather_at(series(), eta)

    assert weather == Weather(
        wind_mph=10.0 + picked_hour,
        gust_mph=20.0 + picked_hour,
        rain_in_hr=pytest.approx(0.01 * picked_hour),
        snow_in_hr=0.0,
    )


def test_rain_includes_showers():
    weather = weather_at(
        series(rain_in_hr=[0.1, 0.2, 0, 0], showers_in_hr=[0.05, 0.15, 0, 0]),
        START + timedelta(minutes=30),
    )

    assert weather.rain_in_hr == pytest.approx(0.35)


def test_eta_past_the_last_forecast_hour_has_no_forecast():
    # 4 hours: 9:00 .. 12:00. 12:30 would need 13:00.
    weather = weather_at(series(hours=4), START + timedelta(hours=3, minutes=30))

    assert weather == NoForecast("The forecast does not reach Mon 16 Nov 13:00 UTC.")


def test_a_missing_value_means_no_forecast():
    weather = weather_at(series(snow_in_hr=[0.0, None, 0.0, 0.0]), START + timedelta(minutes=30))

    assert weather == NoForecast("The forecast has no snow value for Mon 16 Nov 10:00 UTC.")


def test_a_missing_gust_does_not_block_the_forecast():
    # Gusts are only shown; wind, rain and snow decide the risk.
    weather = weather_at(series(gust_mph=[None] * 4), START + timedelta(minutes=30))

    assert isinstance(weather, Weather)
    assert weather.gust_mph is None


def test_eta_before_the_first_forecast_hour_has_no_forecast():
    weather = weather_at(series(), START - timedelta(hours=2))

    assert weather == NoForecast("The forecast starts after Mon 16 Nov 07:00 UTC.")
