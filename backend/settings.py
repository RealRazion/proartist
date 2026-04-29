from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Environment Variable Validation
def get_env(key, default=None, required=False, cast_type=str):
    """
    Sichere Environment Variable Loader mit Validierung
    
    Args:
        key: Environment Variable Name
        default: Fallback Wert
        required: Wenn True, wirft Fehler wenn nicht vorhanden
        cast_type: Type Casting (str, bool, int, list)
    """
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"FEHLER: Erforderliche Environment Variable '{key}' nicht gesetzt!")
    
    if value is None:
        return default
    
    # Type Casting
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        return int(value)
    elif cast_type == list:
        return [item.strip() for item in value.split(',') if item.strip()]
    
    return value

DEBUG = get_env('DEBUG', 'False', cast_type=bool)
ENVIRONMENT = get_env('ENVIRONMENT', 'development')

# Kritische Variablen validieren
SECRET_KEY = get_env('SECRET_KEY')
if not SECRET_KEY:
    is_production = ENVIRONMENT.lower() in ('production', 'prod') and not DEBUG
    if is_production:
        raise ValueError("FEHLER: Erforderliche Environment Variable 'SECRET_KEY' nicht gesetzt!")
    SECRET_KEY = 'dev-insecure-secret-key-change-me'
    logger.warning("SECRET_KEY fehlt. Unsicherer Fallback wird nur fuer nicht-Production verwendet.")

# Warnung wenn DEBUG in Production
if DEBUG and ENVIRONMENT != 'development':
    logger.warning('⚠️  DEBUG=True in PRODUCTION Environment! Dies ist ein Sicherheitsrisiko.')

ALLOWED_HOSTS = get_env(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,proartist.onrender.com',
    cast_type=list
)

# Logging Konfiguration für Startup
logger.info(f"✓ Django Settings geladen (ENVIRONMENT={ENVIRONMENT}, DEBUG={DEBUG})")
logger.info(f"✓ ALLOWED_HOSTS: {ALLOWED_HOSTS}")


INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","rest_framework_simplejwt","django.contrib.staticfiles",
    "corsheaders","rest_framework","channels","core",
]
ASGI_APPLICATION = "backend.asgi.application"

# Channel Layer (dev: InMemory; prod: Redis)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
        # Prod-Beispiel:
        # "BACKEND": "channels_redis.core.RedisChannelLayer",
        # "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    }
}
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"
TEMPLATES = [{
    "BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],
    "APP_DIRS":True,"OPTIONS":{"context_processors":[
        "django.template.context_processors.debug","django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages",],},},]
WSGI_APPLICATION = "backend.wsgi.application"

import dj_database_url
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

LANGUAGE_CODE="de-de"; TIME_ZONE="Europe/Berlin"; USE_I18N=True; USE_TZ=True
STATIC_URL="/static/"; MEDIA_URL="/media/"; MEDIA_ROOT=BASE_DIR/"media"

_cors_origins = [origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()]
if _cors_origins:
    CORS_ALLOWED_ORIGINS = _cors_origins
    CORS_ALLOW_ALL_ORIGINS = False
    CSRF_TRUSTED_ORIGINS = _cors_origins
else:
    CORS_ALLOWED_ORIGINS = [
        "https://proartist.pages.dev",
        "https://localhost",
        "capacitor://localhost",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    CORS_ALLOW_ALL_ORIGINS = False
    CSRF_TRUSTED_ORIGINS = [
        "https://proartist.pages.dev",
        "https://localhost",
    ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-xsrf-token",
]

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

REST_FRAMEWORK = {
  "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
  "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
  "DEFAULT_THROTTLE_CLASSES": (
      "rest_framework.throttling.AnonRateThrottle",
      "rest_framework.throttling.UserRateThrottle",
  ),
  "DEFAULT_THROTTLE_RATES": {
      "anon": os.getenv("THROTTLE_ANON", "500/hour"),
      "user": os.getenv("THROTTLE_USER", "2000/hour"),
  },
}

# API Center (kann per ENV deaktiviert werden)
API_CENTER_OFFLINE = os.getenv("API_CENTER_OFFLINE", "True").lower() in {"1", "true", "yes", "on"}

# Security headers (konfigurierbar per ENV)
SECURE_HSTS_SECONDS = int(os.getenv("HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("HSTS_INCLUDE_SUBDOMAINS", "False") == "True"
SECURE_HSTS_PRELOAD = os.getenv("HSTS_PRELOAD", "False") == "True"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv("REFERRER_POLICY", "same-origin")
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False") == "True"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
