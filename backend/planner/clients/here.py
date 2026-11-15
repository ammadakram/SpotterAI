"""HERE Routing and Autosuggest. Turns HERE's JSON into domain types."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

import flexpolyline
import httpx

from planner.domain.types import LonLat, Piece, Route
from planner.errors import NoRouteFound, RoutingUnavailable

logger = logging.getLogger(__name__)

ROUTES_URL = "https://router.hereapi.com/v8/routes"
AUTOSUGGEST_URL = "https://autosuggest.search.hereapi.com/v1/autosuggest"
# The brief's load is cargo only; HERE needs the whole truck. A typical tractor-trailer
# weighs about 35,000 lb empty.
TRUCK_TARE_LB = 35_000
KG_PER_LB = 0.45359237
# Autosuggest needs a reference point; the centre of the contiguous US keeps results neutral.
US_CENTRE = "39.8,-98.6"
MAX_PLACES = 5


@dataclass(frozen=True)
class Place:
    label: str
    lon: float
    lat: float


class HereClient:
    def __init__(self, api_key: str, http: httpx.Client):
        self._api_key = api_key
        self._http = http

    def get_truck_routes(
        self, origin: LonLat, destination: LonLat, departure: datetime, load_lb: int
    ) -> list[Route]:
        params = {
            "transportMode": "truck",
            "origin": _lat_lng(origin),
            "destination": _lat_lng(destination),
            "departureTime": departure.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alternatives": 2,  # plus the main route = 3 routes
            "return": "polyline,summary",
            # segmentId splits spans at every road segment (~0.5 km); without it HERE merges them.
            "spans": "segmentId,length,duration",
            "vehicle[grossWeight]": round((load_lb + TRUCK_TARE_LB) * KG_PER_LB),
        }
        return parse_routes(
            self._get(ROUTES_URL, params, "Truck routing is unavailable right now.")
        )

    def suggest_places(self, query: str) -> list[Place]:
        params = {"q": query, "in": "countryCode:USA", "at": US_CENTRE, "limit": MAX_PLACES}
        return parse_places(
            self._get(AUTOSUGGEST_URL, params, "Place search is unavailable right now.")
        )

    def _get(self, url: str, params: dict, failure_message: str) -> dict:
        # Never log the request URL or httpx's error text: both contain the API key.
        try:
            response = self._http.get(url, params={**params, "apiKey": self._api_key})
        except httpx.HTTPError as exc:
            logger.warning("HERE request to %s failed: %s", url, type(exc).__name__)
            raise RoutingUnavailable(failure_message) from None
        if response.status_code != 200:
            logger.warning("HERE %s returned %s: %.300s", url, response.status_code, response.text)
            raise RoutingUnavailable(failure_message)
        try:
            return response.json()
        except ValueError:
            logger.warning("HERE %s returned a body that is not JSON", url)
            raise RoutingUnavailable(failure_message) from None


def _lat_lng(point: LonLat) -> str:
    lon, lat = point
    return f"{lat},{lon}"


def parse_places(data: dict) -> list[Place]:
    """Autosuggest response -> places. Items without a position are search-term
    suggestions, not places, so they are skipped."""
    try:
        return [
            Place(
                label=item["address"]["label"],
                lon=_number(item["position"]["lng"]),
                lat=_number(item["position"]["lat"]),
            )
            for item in data["items"]
            if "position" in item
        ]
    except (KeyError, TypeError, ValueError) as exc:
        logger.warning("Unreadable HERE autosuggest response: %r", exc)
        raise RoutingUnavailable("The place search sent a response we could not read.") from exc


def parse_routes(data: dict) -> list[Route]:
    """HERE Routing v8 response -> routes. HERE's JSON is untrusted: anything odd fails loudly."""
    try:
        # "No route" is not an HTTP error at HERE: it is a 200 with no routes and a notice.
        notice_codes = {notice.get("code") for notice in data.get("notices", [])}
        if not data["routes"]:
            if "noRouteFound" in notice_codes:
                raise NoRouteFound("No truck route found between these places.")
            raise ValueError(f"no routes and no noRouteFound notice (notices: {notice_codes})")
        # A critical notice means HERE could only route by breaking a truck restriction
        # (weight, height, hazmat...). Such a route is not one a truck may drive.
        legal = [route for route in data["routes"] if not _has_critical_notice(route)]
        if not legal:
            raise NoRouteFound("No legal truck route found between these places.")
        if len(legal) < len(data["routes"]):
            logger.info(
                "Dropped %d HERE route(s) with critical notices", len(data["routes"]) - len(legal)
            )
        return [_parse_route(route) for route in legal]
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        # The message holds only response data (never the request URL with its key).
        logger.warning("Unreadable HERE routes response: %r", exc)
        raise RoutingUnavailable("The routing service sent a response we could not read.") from exc


def _decode_polyline(encoded: str) -> list[tuple[float, float]]:
    try:
        return flexpolyline.decode(encoded)
    except RuntimeError as exc:  # a truncated string surfaces as "generator raised StopIteration"
        raise ValueError(f"polyline cannot be decoded: {exc}") from exc


def _has_critical_notice(route: dict) -> bool:
    return any(
        notice["severity"] == "critical"
        for section in route["sections"]
        for notice in section.get("notices", [])
    )


def _parse_route(route: dict) -> Route:
    (section,) = route["sections"]  # we never ask for stops, so HERE sends one section
    # HERE's polyline decodes to (lat, lng); the rest of the app uses (lon, lat).
    points = tuple((lng, lat) for lat, lng in _decode_polyline(section["polyline"]))
    pieces = tuple(
        Piece(
            start_index=span["offset"],
            length_m=_number_at_least_zero(span["length"]),
            duration_s=_number_at_least_zero(span["duration"]),
        )
        for span in section["spans"]
    )

    offsets = [piece.start_index for piece in pieces]
    if len(points) < 2 or not pieces:
        raise ValueError("route has no line or no spans")
    # Each piece must start where the previous one left off and have at least one line segment.
    if offsets[0] != 0 or offsets[-1] >= len(points) - 1:
        raise ValueError(
            f"span offsets {offsets[0]}..{offsets[-1]} do not fit {len(points)} points"
        )
    if any(a >= b for a, b in zip(offsets, offsets[1:], strict=False)):
        raise ValueError("span offsets are not increasing")
    return Route(points=points, pieces=pieces)


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"expected a number, got {value!r}")
    return value


def _number_at_least_zero(value: object) -> float:
    if _number(value) < 0:
        raise ValueError(f"expected a number >= 0, got {value!r}")
    return value
