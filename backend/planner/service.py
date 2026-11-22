"""The one entry point for planning a trip. I/O comes in as arguments so tests can fake it."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from planner.domain.assess import assess_route
from planner.domain.checkpoints import SPACINGS_MI, place_checkpoints
from planner.domain.corridor import corridor_cells
from planner.domain.forecast import weather_at
from planner.domain.heatmap import heatmap_frames
from planner.domain.ranking import RankCandidate, Ranking, rank
from planner.domain.risk import classify
from planner.domain.types import (
    Heatmap,
    HourlySeries,
    LonLat,
    NoForecast,
    RatedCheckpoint,
    RiskLevel,
    Route,
    RouteAssessment,
)
from planner.errors import TripTooLarge, WeatherUnavailable


class RoutingProvider(Protocol):
    def get_truck_routes(
        self, origin: LonLat, destination: LonLat, departure: datetime, load_lb: int
    ) -> list[Route]: ...


class WeatherProvider(Protocol):
    def get_hourly(self, points: list[LonLat]) -> list[HourlySeries]: ...


@dataclass(frozen=True)
class PlanRequest:
    origin: LonLat
    destination: LonLat
    departure: datetime
    load_lb: int
    spacing_mi: int


@dataclass(frozen=True)
class PlannedRoute:
    id: str
    label: str
    route: Route
    arrival: datetime
    checkpoints: list[RatedCheckpoint]
    assessment: RouteAssessment


@dataclass(frozen=True)
class Plan:
    generated_at: datetime
    routes: list[PlannedRoute]
    ranking: Ranking
    heatmap: Heatmap


def plan_trip(
    request: PlanRequest, *, routing: RoutingProvider, weather: WeatherProvider, now: datetime
) -> Plan:
    routes = routing.get_truck_routes(
        request.origin, request.destination, request.departure, request.load_lb
    )
    checkpoints = [place_checkpoints(r, request.spacing_mi, request.departure) for r in routes]

    cells = corridor_cells([r.points for r in routes])

    # One weather pass for every checkpoint of every route and every heatmap cell: the client
    # removes repeats (routes share most of their places) and batches the rest.
    checkpoint_points = [
        c.coordinates for route_checkpoints in checkpoints for c in route_checkpoints
    ]
    try:
        all_series = weather.get_hourly(checkpoint_points + cells)
    except TripTooLarge as exc:
        raise _with_advice(exc, request.spacing_mi) from exc
    series = iter(all_series[: len(checkpoint_points)])
    cell_series = dict(zip(cells, all_series[len(checkpoint_points) :], strict=True))

    planned = []
    for i, (route, route_checkpoints) in enumerate(zip(routes, checkpoints, strict=True)):
        rated = []
        for checkpoint in route_checkpoints:
            hour = weather_at(next(series), checkpoint.eta)
            rated.append(
                RatedCheckpoint(
                    checkpoint=checkpoint,
                    weather=None if isinstance(hour, NoForecast) else hour,
                    risk=classify(hour, request.load_lb),
                )
            )
        if all(r.risk.level == RiskLevel.NO_FORECAST for r in rated):
            # Even the departure hour has no forecast: Open-Meteo's data is unusable.
            raise WeatherUnavailable("The weather forecast has no usable data for this trip.")
        planned.append(
            PlannedRoute(
                id=f"r{i + 1}",
                label=f"Route {'ABCDEFG'[i]}",
                route=route,
                arrival=request.departure + timedelta(seconds=route.duration_s),
                checkpoints=rated,
                assessment=assess_route(rated),
            )
        )

    ranking = rank([RankCandidate(p.id, p.assessment, p.route.duration_s) for p in planned])
    return Plan(
        generated_at=now,
        routes=planned,
        ranking=ranking,
        heatmap=heatmap_frames(cell_series, now, request.load_lb),
    )


def _with_advice(exc: TripTooLarge, spacing_mi: int) -> TripTooLarge:
    """Say what the user can do. The heatmap's cells don't depend on the spacing, so at the
    widest spacing there is nothing left to change."""
    if spacing_mi < max(SPACINGS_MI):
        return TripTooLarge(f"{exc.message} Choose a larger checkpoint spacing.", exc.details)
    places = exc.details["places"]
    return TripTooLarge(
        f"This trip is too long for the free weather service: it needs weather for {places} "
        f"places, more than the service allows per minute.",
        exc.details,
    )
