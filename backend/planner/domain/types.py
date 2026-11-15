"""Plain data types shared by the domain functions. No Django, no HTTP."""

from dataclasses import dataclass
from datetime import datetime

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
