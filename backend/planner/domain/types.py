"""Plain data types shared by the domain functions. No Django, no HTTP."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

LonLat = tuple[float, float]


@dataclass(frozen=True)
class Piece:
    """One stretch of road as HERE reports it (a "span")."""

    start_index: int  # index into Route.points where this piece starts
    length_m: float
    duration_s: float


@dataclass(frozen=True)
class Route:
    points: tuple[LonLat, ...]
    pieces: tuple[Piece, ...]

    @property
    def distance_m(self) -> float:
        return sum(piece.length_m for piece in self.pieces)

    @property
    def duration_s(self) -> float:
        return sum(piece.duration_s for piece in self.pieces)


@dataclass(frozen=True)
class Checkpoint:
    mile: float
    coordinates: LonLat
    eta: datetime
    covers_mi: tuple[float, float]  # the stretch this checkpoint speaks for: midpoint to midpoint
    covers_time: tuple[datetime, datetime]  # when the truck enters and leaves that stretch


class RiskLevel(StrEnum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE"
    NO_TRAVEL = "NO_TRAVEL"
    NO_FORECAST = "NO_FORECAST"


@dataclass(frozen=True)
class Weather:
    """One hour of weather at one place. Rain already includes showers."""

    wind_mph: float
    gust_mph: float | None  # shown only; Open-Meteo may lack it
    rain_in_hr: float
    snow_in_hr: float


@dataclass(frozen=True)
class NoForecast:
    """Why there is no usable weather for a checkpoint's hour."""

    reason: str


@dataclass(frozen=True)
class CheckpointRisk:
    level: RiskLevel  # worst of the three conditions, or NO_FORECAST
    wind: RiskLevel | None  # None only when there is no forecast
    rain: RiskLevel | None
    snow: RiskLevel | None
    is_load_escalated: bool  # the load rules raised the checkpoint's level
    no_forecast_reason: str | None = None


@dataclass(frozen=True)
class HourlySeries:
    """Open-Meteo hourly values for one place. Value i is for the hour ending at start + i h
    (rain and snow are that hour's totals). A value is None when Open-Meteo has none."""

    start: datetime
    wind_mph: list[float | None]
    gust_mph: list[float | None]
    rain_in_hr: list[float | None]
    showers_in_hr: list[float | None]
    snow_in_hr: list[float | None]


@dataclass(frozen=True)
class RatedCheckpoint:
    checkpoint: Checkpoint
    weather: Weather | None  # None when there is no forecast for its hour
    risk: CheckpointRisk


@dataclass(frozen=True)
class Stretch:
    """Consecutive road with one risk level."""

    level: RiskLevel
    from_mi: float
    to_mi: float
    starts_at: datetime
    ends_at: datetime


@dataclass(frozen=True)
class RouteAssessment:
    risk_miles: dict[RiskLevel, float]  # every level, NO_FORECAST = unknown miles
    average_risk: float  # 0 (Low) .. 4 (No Travel), over the miles that have a forecast
    stretches: list[Stretch]  # cover the whole route, in order
    is_drivable: bool  # no No Travel anywhere


@dataclass(frozen=True)
class HeatmapCell:
    """One grid cell's hourly values. A value is None when that hour has no forecast."""

    center: LonLat
    risk: list[RiskLevel]  # NO_FORECAST when the hour has no forecast
    wind_mph: list[float | None]
    rain_in_hr: list[float | None]
    snow_in_hr: list[float | None]


@dataclass(frozen=True)
class Heatmap:
    starts_at: datetime  # hour 0
    cells: list[HeatmapCell]
