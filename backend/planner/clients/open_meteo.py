"""Open-Meteo hourly forecasts: batched, parallel, cached by rounded location."""

import logging
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import httpx
from django.core.cache import BaseCache

from planner.domain.types import HourlySeries, LonLat
from planner.errors import TripTooLarge, WeatherUnavailable

logger = logging.getLogger(__name__)

# Variable -> the unit we ask for and check in the answer.
VARIABLES = {
    "wind_speed_10m": "mp/h",
    "wind_gusts_10m": "mp/h",
    "rain": "inch",
    "showers": "inch",
    "snowfall": "inch",
}
# Every place is fetched for the same fixed range from the current hour, so a cached
# entry covers any plan (departure up to +48 h plus the trip).
FORECAST_HOURS = 96
# ~3 mi, close to the forecast model's own resolution: nearby checkpoints share a forecast.
SNAP_DEG = 0.05
PLACES_PER_REQUEST = 100  # keeps the URL around 2 KB
MAX_PARALLEL_REQUESTS = 4
CACHE_SECONDS = 30 * 60
# The free plan allows 600 places per minute per IP. A plan that needs more can never finish,
# and trying would use up the minute for everyone, so it is refused before any request.
# 550 leaves room for other plans in the same minute. A paid key has no minute limit.
FREE_PLAN_MAX_NEW_PLACES = 550

UNAVAILABLE = "Weather data is unavailable right now."
RATE_LIMITED = "The weather service's request limit was reached. Try again in a minute."


def snap(point: LonLat) -> LonLat:
    lon, lat = point
    return (round(round(lon / SNAP_DEG) * SNAP_DEG, 2), round(round(lat / SNAP_DEG) * SNAP_DEG, 2))


class OpenMeteoClient:
    def __init__(self, http: httpx.Client, base_url: str, api_key: str | None, cache: BaseCache):
        self._http = http
        self._url = f"{base_url}/v1/forecast"
        self._api_key = api_key
        self._cache = cache

    def get_hourly(self, points: list[LonLat]) -> list[HourlySeries]:
        """One series per point, in the same order. Points are snapped to SNAP_DEG first."""
        snapped = [snap(p) for p in points]
        found: dict[LonLat, HourlySeries | None] = {
            p: self._cache.get(_cache_key(p)) for p in dict.fromkeys(snapped)
        }
        missing = [p for p, series in found.items() if series is None]
        if not self._api_key and len(missing) > FREE_PLAN_MAX_NEW_PLACES:
            raise TripTooLarge(
                f"This trip needs weather for {len(missing)} places, more than the free weather "
                f"service allows per minute.",
                {"places": len(missing), "limit": FREE_PLAN_MAX_NEW_PLACES},
            )
        batches = [
            missing[i : i + PLACES_PER_REQUEST] for i in range(0, len(missing), PLACES_PER_REQUEST)
        ]
        if batches:
            with ThreadPoolExecutor(max_workers=min(len(batches), MAX_PARALLEL_REQUESTS)) as pool:
                # map() re-raises the first failure; only successful batches get cached.
                for batch, results in zip(batches, pool.map(self._fetch, batches), strict=True):
                    for point, series in zip(batch, results, strict=True):
                        found[point] = series
                        self._cache.set(_cache_key(point), series, CACHE_SECONDS)
        return [found[p] for p in snapped]

    def _fetch(self, points: list[LonLat]) -> list[HourlySeries]:
        params = {
            "latitude": ",".join(f"{lat:.2f}" for _, lat in points),
            "longitude": ",".join(f"{lon:.2f}" for lon, _ in points),
            "hourly": ",".join(VARIABLES),
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "GMT",
            "forecast_hours": FORECAST_HOURS,
        }
        if self._api_key:
            params["apikey"] = self._api_key
        # Never log the URL or httpx's error text: with a paid plan they contain the key.
        try:
            response = self._http.get(self._url, params=params)
        except httpx.HTTPError as exc:
            logger.warning("Open-Meteo request failed: %s", type(exc).__name__)
            raise WeatherUnavailable(UNAVAILABLE) from None
        if response.status_code == 429:
            logger.warning("Open-Meteo rate limit: %.300s", response.text)
            raise WeatherUnavailable(RATE_LIMITED)
        if response.status_code != 200:
            logger.warning("Open-Meteo returned %s: %.300s", response.status_code, response.text)
            raise WeatherUnavailable(UNAVAILABLE)

        try:
            data = response.json()
            places = [data] if isinstance(data, dict) else data  # one place comes as an object
            if not isinstance(places, list) or len(places) != len(points):
                raise ValueError(f"asked for {len(points)} places, got {len(places)}")
            return [_parse_series(place) for place in places]
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("Unreadable Open-Meteo response: %r", exc)
            raise WeatherUnavailable(UNAVAILABLE) from exc


def _cache_key(point: LonLat) -> str:
    return f"open-meteo:{point[0]:.2f},{point[1]:.2f}"


def _parse_series(place: dict) -> HourlySeries:
    units, hourly = place["hourly_units"], place["hourly"]
    for name, unit in VARIABLES.items():
        if units[name] != unit:
            raise ValueError(f"{name} is in {units[name]!r}, expected {unit!r}")

    times = [datetime.fromisoformat(t).replace(tzinfo=UTC) for t in hourly["time"]]
    if not times or any(
        b - a != timedelta(hours=1) for a, b in zip(times, times[1:], strict=False)
    ):
        raise ValueError("hours are missing or not consecutive")
    columns = {name: hourly[name] for name in VARIABLES}
    for name, values in columns.items():
        if len(values) != len(times):
            raise ValueError(f"{name} has {len(values)} values for {len(times)} hours")
        if any(v is not None and not _is_amount(v) for v in values):
            raise ValueError(f"{name} has a value that is not a number >= 0")

    return HourlySeries(
        start=times[0],
        wind_mph=columns["wind_speed_10m"],
        gust_mph=columns["wind_gusts_10m"],
        rain_in_hr=columns["rain"],
        showers_in_hr=columns["showers"],
        snow_in_hr=columns["snowfall"],
    )


def _is_amount(value: object) -> bool:
    # json accepts NaN and Infinity; NaN would fail every band check and read as Low.
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )
