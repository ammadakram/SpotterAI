"""Thin views: validate input, call the service, serialize. No logic here."""

import functools

import httpx
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from planner.clients.here import HereClient
from planner.clients.open_meteo import OpenMeteoClient
from planner.serializers import PlanRequestSerializer, plan_to_json
from planner.service import plan_trip

MAX_QUERY_LENGTH = 100


def _http_client() -> httpx.Client:
    timeout = httpx.Timeout(settings.HTTP_READ_TIMEOUT_S, connect=settings.HTTP_CONNECT_TIMEOUT_S)
    return httpx.Client(timeout=timeout)


@functools.cache
def here_client() -> HereClient:
    return HereClient(settings.HERE_API_KEY, _http_client())


@functools.cache
def weather_client() -> OpenMeteoClient:
    return OpenMeteoClient(
        _http_client(),
        base_url=settings.OPEN_METEO_BASE_URL,
        api_key=settings.OPEN_METEO_API_KEY,
        cache=cache,
    )


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def places(request):
    query = request.query_params.get("q", "").strip()
    if not query:
        raise ValidationError({"q": ["Type a place to search for."]})
    if len(query) > MAX_QUERY_LENGTH:
        raise ValidationError({"q": [f"Use at most {MAX_QUERY_LENGTH} characters."]})
    found = here_client().suggest_places(query)
    return Response({"places": [{"label": p.label, "lon": p.lon, "lat": p.lat} for p in found]})


@api_view(["POST"])
def plans(request):
    current_time = now()
    serializer = PlanRequestSerializer(data=request.data, context={"now": current_time})
    serializer.is_valid(raise_exception=True)
    plan = plan_trip(
        serializer.to_request(), routing=here_client(), weather=weather_client(), now=current_time
    )
    return Response(plan_to_json(plan))
