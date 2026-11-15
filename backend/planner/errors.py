"""Errors that reach the user. Each maps to one code and HTTP status in the error shape."""

import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf
from rest_framework.exceptions import APIException, ParseError, ValidationError
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class AppError(Exception):
    code = "INTERNAL_ERROR"
    status = 500

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NoRouteFound(AppError):
    code = "NO_ROUTE_FOUND"
    status = 422


class RoutingUnavailable(AppError):
    code = "ROUTING_UNAVAILABLE"
    status = 502


class WeatherUnavailable(AppError):
    code = "WEATHER_UNAVAILABLE"
    status = 502


def api_exception_handler(exc: Exception, context: dict) -> Response:
    """DRF exception handler: every error leaves the API in the same shape."""
    # DRF's default handler converts these two Django exceptions; ours must too.
    if isinstance(exc, Http404):
        exc = drf.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = drf.PermissionDenied()
    if isinstance(exc, AppError):
        return _error(exc.status, exc.code, exc.message, exc.details)
    if isinstance(exc, ValidationError):
        details = exc.detail if isinstance(exc.detail, dict) else {"nonField": exc.detail}
        return _error(400, "VALIDATION_ERROR", _first_message(details), details)
    if isinstance(exc, ParseError):
        return _error(400, "VALIDATION_ERROR", "The request body is not valid JSON.", {})
    if isinstance(exc, APIException):
        return _error(exc.status_code, exc.default_code.upper(), str(exc.detail), {})
    logger.exception("Unhandled error in %s", context["view"].__class__.__name__)
    return _error(500, "INTERNAL_ERROR", "Something went wrong on our side.", {})


def _error(status: int, code: str, message: str, details: dict) -> Response:
    return Response({"error": {"code": code, "message": message, "details": details}}, status)


def _first_message(details: dict | list, path: str = "") -> str:
    """The first leaf message, prefixed with the field it belongs to: "origin.lat: ..."."""
    if isinstance(details, dict):
        field, value = next(iter(details.items()))
        return _first_message(value, f"{path}.{field}" if path else field)
    first = details[0]
    if isinstance(first, dict | list):
        return _first_message(first, path)
    return f"{path}: {first}" if path and path != "nonField" else str(first)
