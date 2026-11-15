"""Django settings. All configuration comes from environment variables (see .env.example)."""

import logging
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(
            f"Missing required environment variable {name} (see .env.example)."
        )
    return value


def list_env(name: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


SECRET_KEY = require_env("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = list_env("ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS = list_env("CORS_ALLOWED_ORIGINS")

# Third-party services
HERE_API_KEY = require_env("HERE_API_KEY")
OPEN_METEO_BASE_URL = os.environ.get("OPEN_METEO_BASE_URL", "https://api.open-meteo.com")
OPEN_METEO_API_KEY = os.environ.get("OPEN_METEO_API_KEY", "")
HTTP_CONNECT_TIMEOUT_S = 5
HTTP_READ_TIMEOUT_S = 15

# No database: the API computes everything per request and stores nothing.
DATABASES = {}

INSTALLED_APPS = [
    "corsheaders",
    "rest_framework",
    "planner",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "planner.errors.api_exception_handler",
}

# In-process cache for weather responses (no shared cache needed for one server process).
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

USE_TZ = True
TIME_ZONE = "UTC"

# httpx logs every request URL at INFO, and HERE's URLs carry the API key. Keep it at WARNING
# so no future logging setup can write the key to the logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
