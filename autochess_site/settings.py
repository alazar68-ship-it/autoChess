from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _env(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key)
    return value if value is not None else default

def _env_bool(key: str, default: bool = False) -> bool:
    value = _env(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

DEBUG = _env_bool("DJANGO_DEBUG", True)

SECRET_KEY = _env("DJANGO_SECRET_KEY", "dev-(KG)@cEA#HbQGTAAP+(ph2aljdU53Yp8rWLZfv&i6$fn")  # For dev; override in prod.
ALLOWED_HOSTS = [h.strip() for h in (_env("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost") or "").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "arena.apps.ArenaConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "autochess_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "arena.context_processors.autochess_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "autochess_site.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            # Wait for locks instead of failing fast (helps with rare concurrent writes on demos).
            "timeout": 20,  # seconds
        },
    }
}

# SQLite does not benefit from long-lived connections; keep them short.
CONN_MAX_AGE = 0


AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "hu"
TIME_ZONE = "Europe/Budapest"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# AutoChess config
AUTOCHESS_STOCKFISH_PATH = _env("AUTOCHESS_STOCKFISH_PATH", "stockfish") or "stockfish"
AUTOCHESS_DEFAULT_MOVETIME_MS = int(_env("AUTOCHESS_DEFAULT_MOVETIME_MS", "150") or "150")
AUTOCHESS_MAX_PLIES = int(_env("AUTOCHESS_MAX_PLIES", "600") or "600")
AUTOCHESS_PREVIEW_MS = int(os.getenv('AUTOCHESS_PREVIEW_MS', '350'))

CSRF_TRUSTED_ORIGINS = [
    "https://lazarsoft.hu",
    "https://www.lazarsoft.hu",
]
