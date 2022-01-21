"""
Django settings for benefits project.
"""
import os


def _filter_empty(ls):
    return [s for s in ls if s]


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ADMIN = os.environ.get("DJANGO_ADMIN", "False").lower() == "true"

ALLOWED_HOSTS = _filter_empty(os.environ["DJANGO_ALLOWED_HOSTS"].split(","))

# Application definition

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "benefits.core",
    "benefits.enrollment",
    "benefits.eligibility",
]

if ADMIN:
    INSTALLED_APPS.extend(
        [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.messages",
        ]
    )

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "benefits.core.middleware.Healthcheck",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "benefits.core.middleware.ChangedLanguageEvent",
]

if ADMIN:
    MIDDLEWARE.extend(
        [
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ]
    )

if DEBUG:
    MIDDLEWARE.extend(["benefits.core.middleware.DebugSession"])

CSRF_COOKIE_AGE = None
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = _filter_empty(os.environ["DJANGO_TRUSTED_ORIGINS"].split(","))

SESSION_COOKIE_SAMESITE = "Strict"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    CSRF_FAILURE_VIEW = "benefits.core.views.csrf_failure"
    SESSION_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True

ROOT_URLCONF = "benefits.urls"

template_ctx_processors = [
    "django.template.context_processors.request",
    "benefits.core.context_processors.analytics",
]

if DEBUG:
    template_ctx_processors.extend(
        [
            "django.template.context_processors.debug",
            "benefits.core.context_processors.debug",
        ]
    )

if ADMIN:
    template_ctx_processors.extend(
        [
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]
    )

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "benefits", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": template_ctx_processors,
        },
    },
]

WSGI_APPLICATION = "benefits.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB", "django") + ".db",
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = []

if ADMIN:
    AUTH_PASSWORD_VALIDATORS.extend(
        [
            {
                "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
            },
        ]
    )

# Internationalization

LANGUAGE_CODE = "en"

LANGUAGE_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_SAMESITE = "Strict"
LANGUAGE_COOKIE_SECURE = True

LANGUAGES = [("en", "English"), ("es", "Español")]

LOCALE_PATHS = [os.path.join(BASE_DIR, "benefits", "locale")]

USE_I18N = True
USE_L10N = True

TIME_ZONE = "UTC"
USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "benefits", "static")]
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Logging configuration

LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "DEBUG" if DEBUG else "WARNING")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[{asctime}] {levelname} {name}:{lineno} {message}",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "default": {"class": "logging.StreamHandler", "formatter": "default"},
    },
    "root": {
        "handlers": ["default"],
        "level": LOG_LEVEL,
    },
    "loggers": {"django": {"handlers": ["default"], "propagate": False}},
}

# Analytics configuration

ANALYTICS_KEY = os.environ.get("ANALYTICS_KEY")

# Content Security Policy
# Configuration docs at https://django-csp.readthedocs.io/en/latest/configuration.html

# In particular, note that the inner single-quotes are required!
# https://django-csp.readthedocs.io/en/latest/configuration.html#policy-settings

CSP_DEFAULT_SRC = ["'self'"]

env_connect_src = _filter_empty(os.environ.get("DJANGO_CSP_CONNECT_SRC", "").split(","))
CSP_CONNECT_SRC = ["'self'"]
CSP_CONNECT_SRC.extend(env_connect_src)

env_font_src = _filter_empty(os.environ.get("DJANGO_CSP_FONT_SRC", "").split(","))
CSP_FONT_SRC = list(env_font_src)

CSP_FRAME_ANCESTORS = ["'none'"]
CSP_FRAME_SRC = ["'none'"]

env_script_src = _filter_empty(os.environ.get("DJANGO_CSP_SCRIPT_SRC", "").split(","))
CSP_SCRIPT_SRC = ["'unsafe-inline'"]
CSP_SCRIPT_SRC.extend(env_script_src)

env_style_src = _filter_empty(os.environ.get("DJANGO_CSP_STYLE_SRC", "").split(","))
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_STYLE_SRC.extend(env_style_src)

# rate limit configuration

# number of requests allowed in the given period
RATE_LIMIT = int(os.environ.get("DJANGO_RATE_LIMIT", 0))

# HTTP request methods to rate limit
RATE_LIMIT_METHODS = os.environ.get("DJANGO_RATE_LIMIT_METHODS", "").upper().split(",")

# number of seconds before additional requests are denied
RATE_LIMIT_PERIOD = int(os.environ.get("DJANGO_RATE_LIMIT_PERIOD", 0))
