"""The one entry point for planning a trip. I/O comes in as arguments so tests can fake it."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from planner.domain.assess import assess_route
from planner.domain.checkpoints import place_checkpoints
from planner.domain.forecast import weather_at
from planner.domain.ranking import RankCandidate, Ranking, rank
from planner.domain.risk import classify
from planner.domain.types import (
    HourlySeries,
    LonLat,
    NoForecast,
    RatedCheckpoint,
    RiskLevel,
    Route,
    RouteAssessment,
)
from planner.errors import WeatherUnavailable


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


def plan_trip(
    request: PlanRequest, *, routing: RoutingProvider, weather: WeatherProvider, now: datetime
) -> Plan:
    routes = routing.get_truck_routes(
        request.origin, request.destination, request.departure, request.load_lb
    )
    checkpoints = [place_checkpoints(r, request.spacing_mi, request.departure) for r in routes]

    # One weather call for every checkpoint of every route: routes share most of their places.
    all_points = [c.coordinates for route_checkpoints in checkpoints for c in route_checkpoints]
    series = iter(weather.get_hourly(all_points))

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
    return Plan(generated_at=now, routes=planned, ranking=ranking)
