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
    
    try:
        # Type Casting
        if cast_type == bool:
            return str(value).strip().lower() in ('true', '1', 'yes', 'on')
        elif cast_type == int:
            return int(str(value).strip())
        elif cast_type == list:
            if isinstance(value, (list, tuple)):
                return [str(item).strip() for item in value if str(item).strip()]
            return [item.strip() for item in str(value).split(',') if item.strip()]
        return value
    except (ValueError, TypeError) as exc:
        if required:
            raise ValueError(
                f"FEHLER: Environment Variable '{key}' hat einen ungueltigen Wert fuer {cast_type.__name__}: {value!r}"
            ) from exc
        logger.warning(
            "Ungueltige Environment Variable %s=%r fuer %s. Nutze Fallback %r.",
            key,
            value,
            cast_type.__name__,
            default,
        )
        return default

DEBUG = get_env('DEBUG', 'False', cast_type=bool)
ENVIRONMENT = get_env('ENVIRONMENT', 'development')
ALLOW_TEST_ENDPOINTS = get_env('ALLOW_TEST_ENDPOINTS', 'False', cast_type=bool)

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

# Channel Layer (dev: InMemory; prod: Redis via CHANNEL_REDIS_URL/REDIS_URL)
_redis_channel_url = get_env("CHANNEL_REDIS_URL") or get_env("REDIS_URL")
_channel_capacity = max(10, get_env("CHANNEL_LAYER_CAPACITY", 50, cast_type=int))
_channel_expiry = max(5, get_env("CHANNEL_LAYER_EXPIRY", 15, cast_type=int))
_channel_group_expiry = max(60, get_env("CHANNEL_LAYER_GROUP_EXPIRY", 300, cast_type=int))
if _redis_channel_url:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [_redis_channel_url],
                "capacity": _channel_capacity,
                "expiry": _channel_expiry,
                "group_expiry": _channel_group_expiry,
            },
        }
    }
    logger.info("✓ CHANNEL_LAYERS uses Redis backend")
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
            "CONFIG": {
                "capacity": _channel_capacity,
                "expiry": _channel_expiry,
                "group_expiry": _channel_group_expiry,
            },
        }
    }
    logger.warning(
        "CHANNEL_LAYERS uses InMemory backend. Configure REDIS_URL/CHANNEL_REDIS_URL in production for better stability."
    )
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

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

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

# Upload tuning for low-memory runtimes (e.g. Render starter instances).
# Force uploads to temporary files on disk instead of buffering in RAM.
FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]
FILE_UPLOAD_MAX_MEMORY_SIZE = get_env("FILE_UPLOAD_MAX_MEMORY_SIZE", 256 * 1024, cast_type=int)
DATA_UPLOAD_MAX_MEMORY_SIZE = get_env("DATA_UPLOAD_MAX_MEMORY_SIZE", 10 * 1024 * 1024, cast_type=int)
DATA_UPLOAD_MAX_NUMBER_FIELDS = get_env("DATA_UPLOAD_MAX_NUMBER_FIELDS", 2000, cast_type=int)
MAX_CHAT_FILE_SIZE = get_env("MAX_CHAT_FILE_SIZE", 5 * 1024 * 1024, cast_type=int)
MAX_PROJECT_FILE_SIZE = get_env("MAX_PROJECT_FILE_SIZE", 50 * 1024 * 1024, cast_type=int)
MAX_AUDIO_FILE_SIZE = get_env("MAX_AUDIO_FILE_SIZE", 50 * 1024 * 1024, cast_type=int)
MAX_AVATAR_SIZE = get_env("MAX_AVATAR_SIZE", 2 * 1024 * 1024, cast_type=int)

REST_FRAMEWORK = {
  "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
  "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
  "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%d.%m.%Y",
      "%d/%m/%Y",
      "%d-%m-%Y",
      "%Y/%m/%d",
  ],
  "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": get_env("API_PAGE_SIZE", 50, cast_type=int),
  "DEFAULT_THROTTLE_CLASSES": (
      "rest_framework.throttling.AnonRateThrottle",
      "rest_framework.throttling.UserRateThrottle",
  ),
  "DEFAULT_THROTTLE_RATES": {
      "anon": os.getenv("THROTTLE_ANON", "500/hour"),
      "user": os.getenv("THROTTLE_USER", "2000/hour"),
            "register": os.getenv("THROTTLE_REGISTER", "10/hour"),
            "verify_registration": os.getenv("THROTTLE_VERIFY_REGISTRATION", "20/hour"),
            "set_password": os.getenv("THROTTLE_SET_PASSWORD", "20/hour"),
            "invite_user": os.getenv("THROTTLE_INVITE_USER", "120/hour"),
  },
}

# API Center (kann per ENV deaktiviert werden)
API_CENTER_OFFLINE = os.getenv("API_CENTER_OFFLINE", "True").lower() in {"1", "true", "yes", "on"}

# Security headers (konfigurierbar per ENV)
SECURE_HSTS_SECONDS = get_env("HSTS_SECONDS", 0, cast_type=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_env("HSTS_INCLUDE_SUBDOMAINS", "False", cast_type=bool)
SECURE_HSTS_PRELOAD = get_env("HSTS_PRELOAD", "False", cast_type=bool)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv("REFERRER_POLICY", "same-origin")
CSRF_COOKIE_SECURE = get_env("CSRF_COOKIE_SECURE", "False", cast_type=bool)
SESSION_COOKIE_SECURE = get_env("SESSION_COOKIE_SECURE", "False", cast_type=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email (Gmail SMTP via App-Passwort)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_env('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = get_env('EMAIL_HOST_USER', 'noreply@proartist.app')
