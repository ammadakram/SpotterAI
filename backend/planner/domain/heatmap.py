"""Hourly corridor weather for the 0–48 h slider."""

from datetime import datetime, timedelta

from planner.domain.forecast import weather_at
from planner.domain.risk import classify
from planner.domain.types import Heatmap, HeatmapCell, HourlySeries, LonLat, NoForecast

HEATMAP_HOURS = 49  # now (hour 0) to +48 h
HOUR = timedelta(hours=1)


def heatmap_frames(
    series_by_cell: dict[LonLat, HourlySeries], now: datetime, load_lb: int
) -> Heatmap:
    """Each cell's weather and risk for 49 hours, starting with the hour that contains now.

    An hour is labelled by its end, like Open-Meteo's values: 9:20 is in the hour ending 10:00.
    """
    starts_at = _hour_containing(now)
    hours = [starts_at + h * HOUR for h in range(HEATMAP_HOURS)]
    return Heatmap(
        starts_at=starts_at,
        cells=[_cell(center, series, hours, load_lb) for center, series in series_by_cell.items()],
    )


def _cell(center: LonLat, series: HourlySeries, hours: list[datetime], load_lb: int) -> HeatmapCell:
    weather = [weather_at(series, hour) for hour in hours]
    known = [None if isinstance(w, NoForecast) else w for w in weather]
    return HeatmapCell(
        center=center,
        # Same rules as the checkpoints, load included.
        risk=[classify(w, load_lb).level for w in weather],
        wind_mph=[None if w is None else w.wind_mph for w in known],
        rain_in_hr=[None if w is None else w.rain_in_hr for w in known],
        snow_in_hr=[None if w is None else w.snow_in_hr for w in known],
    )


def _hour_containing(moment: datetime) -> datetime:
    start = moment.replace(minute=0, second=0, microsecond=0)
    return start if start == moment else start + HOUR
