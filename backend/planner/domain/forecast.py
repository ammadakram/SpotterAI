"""Pick the forecast hour for a moment on the road."""

from datetime import datetime, timedelta
from math import ceil

from planner.domain.types import HourlySeries, NoForecast, Weather

HOUR = timedelta(hours=1)


def weather_at(series: HourlySeries, eta: datetime) -> Weather | NoForecast:
    """The weather of the hour the truck is driving in at `eta`.

    Rain and snow at hour T are totals for the hour *ending* at T, so 9:45 uses 10:00.
    """
    index = ceil((eta - series.start) / HOUR)
    hour = series.start + index * HOUR
    if index < 0:
        return NoForecast(f"The forecast starts after {_label(hour)}.")
    if index >= len(series.wind_mph):
        return NoForecast(f"The forecast does not reach {_label(hour)}.")

    # Gusts are only shown, so a missing gust does not block the risk.
    required = {
        "wind": series.wind_mph[index],
        "rain": series.rain_in_hr[index],
        "showers": series.showers_in_hr[index],
        "snow": series.snow_in_hr[index],
    }
    for name, value in required.items():
        if value is None:
            return NoForecast(f"The forecast has no {name} value for {_label(hour)}.")

    return Weather(
        wind_mph=required["wind"],
        gust_mph=series.gust_mph[index],
        rain_in_hr=required["rain"] + required["showers"],
        snow_in_hr=required["snow"],
    )


def _label(hour: datetime) -> str:
    return hour.strftime("%a %-d %b %H:%M UTC")
