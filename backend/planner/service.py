"""The one entry point for planning a trip. I/O comes in as arguments so tests can fake it."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from planner.domain.checkpoints import place_checkpoints
from planner.domain.types import Checkpoint, LonLat, Route


class RoutingProvider(Protocol):
    def get_truck_routes(
        self, origin: LonLat, destination: LonLat, departure: datetime, load_lb: int
    ) -> list[Route]: ...


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
    checkpoints: list[Checkpoint]


@dataclass(frozen=True)
class Plan:
    generated_at: datetime
    routes: list[PlannedRoute]


def plan_trip(request: PlanRequest, *, routing: RoutingProvider, now: datetime) -> Plan:
    routes = routing.get_truck_routes(
        request.origin, request.destination, request.departure, request.load_lb
    )
    planned = [
        PlannedRoute(
            id=f"r{i + 1}",
            label=f"Route {'ABCDEFG'[i]}",
            route=route,
            arrival=request.departure + timedelta(seconds=route.duration_s),
            checkpoints=place_checkpoints(route, request.spacing_mi, request.departure),
        )
        for i, route in enumerate(routes)
    ]
    return Plan(generated_at=now, routes=planned)
