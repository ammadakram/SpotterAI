import pytest

from planner.domain.risk import classify
from planner.domain.types import NoForecast, RiskLevel, Weather

LIGHT_LOAD = 10_000


def calm(**overrides) -> Weather:
    values = {"wind_mph": 5.0, "gust_mph": 10.0, "rain_in_hr": 0.0, "snow_in_hr": 0.0}
    return Weather(**{**values, **overrides})


@pytest.mark.parametrize(
    ("wind_mph", "level"),
    [
        (24.9, RiskLevel.LOW),
        (25, RiskLevel.MODERATE),
        (
            34.5,
            RiskLevel.MODERATE,
        ),  # between the brief's "25–34" and "35–44": bands start at their lower bound
        (35, RiskLevel.HIGH),
        (44.9, RiskLevel.HIGH),
        (45, RiskLevel.SEVERE),
        (54.9, RiskLevel.SEVERE),
        (55, RiskLevel.NO_TRAVEL),
    ],
)
def test_wind_bands(wind_mph, level):
    risk = classify(calm(wind_mph=wind_mph), LIGHT_LOAD)

    assert risk.wind == level
    assert risk.level == level


@pytest.mark.parametrize(
    ("rain_in_hr", "level"),
    [
        (0.09, RiskLevel.LOW),
        (0.10, RiskLevel.MODERATE),
        (0.25, RiskLevel.HIGH),  # in both "0.10–0.25" and "0.25–0.50": the higher band wins
        (0.49, RiskLevel.HIGH),
        (0.50, RiskLevel.SEVERE),
        (1.00, RiskLevel.SEVERE),  # No Travel is "> 1.00"
        (1.01, RiskLevel.NO_TRAVEL),
    ],
)
def test_rain_bands(rain_in_hr, level):
    risk = classify(calm(rain_in_hr=rain_in_hr), LIGHT_LOAD)

    assert risk.rain == level
    assert risk.level == level


@pytest.mark.parametrize(
    ("snow_in_hr", "level"),
    [
        (0.49, RiskLevel.LOW),
        (0.5, RiskLevel.MODERATE),
        (1.0, RiskLevel.HIGH),
        (2.0, RiskLevel.SEVERE),
        (3.0, RiskLevel.SEVERE),  # No Travel is "> 3.0"
        (3.01, RiskLevel.NO_TRAVEL),
    ],
)
def test_snow_bands(snow_in_hr, level):
    risk = classify(calm(snow_in_hr=snow_in_hr), LIGHT_LOAD)

    assert risk.snow == level
    assert risk.level == level


def test_checkpoint_level_is_the_worst_condition():
    risk = classify(calm(wind_mph=30, rain_in_hr=0.30, snow_in_hr=2.5), LIGHT_LOAD)

    assert (risk.wind, risk.rain, risk.snow) == (
        RiskLevel.MODERATE,
        RiskLevel.HIGH,
        RiskLevel.SEVERE,
    )
    assert risk.level == RiskLevel.SEVERE


@pytest.mark.parametrize(
    ("wind_mph", "load_lb", "level", "escalated"),
    [
        (45, 30_000, RiskLevel.SEVERE, False),  # the rule is "> 30,000"
        (45, 30_001, RiskLevel.NO_TRAVEL, True),
        (54.9, 45_000, RiskLevel.NO_TRAVEL, True),
        (35, 40_000, RiskLevel.HIGH, False),  # the rule is "> 40,000"
        (35, 40_001, RiskLevel.SEVERE, True),
        (44.9, 45_000, RiskLevel.SEVERE, True),
        (34.9, 45_000, RiskLevel.MODERATE, False),  # load rules start at 35 mph
        (55, 0, RiskLevel.NO_TRAVEL, False),  # >= 55 mph is No Travel for any load
    ],
)
def test_load_rules_raise_wind(wind_mph, load_lb, level, escalated):
    risk = classify(calm(wind_mph=wind_mph), load_lb)

    assert risk.wind == level
    assert risk.level == level
    assert risk.is_load_escalated is escalated


def test_not_escalated_when_another_condition_was_already_as_bad():
    # The load raises wind from High to Severe, but rain is Severe anyway.
    risk = classify(calm(wind_mph=40, rain_in_hr=0.60), 45_000)

    assert risk.wind == RiskLevel.SEVERE
    assert risk.level == RiskLevel.SEVERE
    assert risk.is_load_escalated is False


def test_no_forecast_is_never_low():
    risk = classify(NoForecast("The forecast does not reach Tue 14:00 UTC."), LIGHT_LOAD)

    assert risk.level == RiskLevel.NO_FORECAST
    assert risk.no_forecast_reason == "The forecast does not reach Tue 14:00 UTC."
    assert (risk.wind, risk.rain, risk.snow) == (None, None, None)
    assert risk.is_load_escalated is False
