"""Risk classification from the brief's table.

A band starts at its lower bound ([lower, next)). The brief writes rain and snow
No Travel as "> 1.00" and "> 3.0", so those two thresholds are strict.
"""

from collections.abc import Callable

from planner.domain.types import CheckpointRisk, NoForecast, RiskLevel, Weather

Band = tuple[Callable[[float], bool], RiskLevel]


def _at_least(threshold: float) -> Callable[[float], bool]:
    return lambda value: value >= threshold


def _above(threshold: float) -> Callable[[float], bool]:
    return lambda value: value > threshold


# Highest band first; anything that matches none is Low.
WIND_BANDS_MPH: list[Band] = [
    (_at_least(55), RiskLevel.NO_TRAVEL),
    (_at_least(45), RiskLevel.SEVERE),
    (_at_least(35), RiskLevel.HIGH),
    (_at_least(25), RiskLevel.MODERATE),
]
RAIN_BANDS_IN_HR: list[Band] = [
    (_above(1.00), RiskLevel.NO_TRAVEL),
    (_at_least(0.50), RiskLevel.SEVERE),
    (_at_least(0.25), RiskLevel.HIGH),
    (_at_least(0.10), RiskLevel.MODERATE),
]
SNOW_BANDS_IN_HR: list[Band] = [
    (_above(3.0), RiskLevel.NO_TRAVEL),
    (_at_least(2.0), RiskLevel.SEVERE),
    (_at_least(1.0), RiskLevel.HIGH),
    (_at_least(0.5), RiskLevel.MODERATE),
]

# Driving risk from least to most; the index is the score used for the average (0..4).
# NO_FORECAST is not on this scale.
SEVERITY = [
    RiskLevel.LOW,
    RiskLevel.MODERATE,
    RiskLevel.HIGH,
    RiskLevel.SEVERE,
    RiskLevel.NO_TRAVEL,
]


# Load rules (the brief): heavier trucks are pushed over by lower winds.
NO_TRAVEL_IN_SEVERE_WIND_ABOVE_LB = 30_000  # 45–54 mph
SEVERE_IN_HIGH_WIND_ABOVE_LB = 40_000  # 35–44 mph


def classify(weather: Weather | NoForecast, load_lb: int) -> CheckpointRisk:
    if isinstance(weather, NoForecast):
        return CheckpointRisk(
            level=RiskLevel.NO_FORECAST,
            wind=None,
            rain=None,
            snow=None,
            is_load_escalated=False,
            no_forecast_reason=weather.reason,
        )
    weather_wind = _band(weather.wind_mph, WIND_BANDS_MPH)
    wind = _apply_load_rules(weather_wind, load_lb)
    rain = _band(weather.rain_in_hr, RAIN_BANDS_IN_HR)
    snow = _band(weather.snow_in_hr, SNOW_BANDS_IN_HR)

    level = _worst(wind, rain, snow)
    # Flag the load only when it changed what the driver sees: the checkpoint's level.
    is_load_escalated = level != _worst(weather_wind, rain, snow)
    return CheckpointRisk(
        level=level, wind=wind, rain=rain, snow=snow, is_load_escalated=is_load_escalated
    )


def _apply_load_rules(wind: RiskLevel, load_lb: int) -> RiskLevel:
    if wind == RiskLevel.SEVERE and load_lb > NO_TRAVEL_IN_SEVERE_WIND_ABOVE_LB:
        return RiskLevel.NO_TRAVEL
    if wind == RiskLevel.HIGH and load_lb > SEVERE_IN_HIGH_WIND_ABOVE_LB:
        return RiskLevel.SEVERE
    return wind


def _worst(*levels: RiskLevel) -> RiskLevel:
    return max(levels, key=SEVERITY.index)


def _band(value: float, bands: list[Band]) -> RiskLevel:
    for matches, level in bands:
        if matches(value):
            return level
    return RiskLevel.LOW
