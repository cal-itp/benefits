"""
Django settings for benefits project.
"""
import os


def _filter_empty(ls):
    return [s for s in ls if s]


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ADMIN = os.environ.get("DJANGO_ADMIN", "False").lower() == "true"

ALLOWED_HOSTS = _filter_empty(os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(","))

# Application definition

INSTALLED_APPS = [
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "benefits.core",
    "benefits.enrollment",
    "benefits.eligibility",
    "benefits.oauth",
]

if ADMIN:
    INSTALLED_APPS.extend(
        [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
        ]
    )

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
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
CSRF_TRUSTED_ORIGINS = _filter_empty(os.environ.get("DJANGO_TRUSTED_ORIGINS", "http://localhost,http://127.0.0.1").split(","))

# With `Strict`, the user loses their Django session between leaving our app to
# sign in with OAuth, and coming back into our app from the OAuth redirect.
# This is because `Strict` disallows our cookie being sent from an external
# domain and so the session cookie is lost.
#
# `Lax` allows the cookie to travel with the user and be sent back to us by the
# OAuth server, as long as the request is "safe" i.e. GET
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = "_benefitssessionid"

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    CSRF_FAILURE_VIEW = "benefits.core.views.csrf_failure"
    SESSION_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True

# the NGINX reverse proxy sits in front of the application in deployed environments
# SSL terminates before getting to Django, and NGINX adds this header to indicate
# if the original request was secure or not
#
# See https://docs.djangoproject.com/en/3.2/ref/settings/#secure-proxy-ssl-header
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ROOT_URLCONF = "benefits.urls"

template_ctx_processors = [
    "django.template.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "benefits.core.context_processors.analytics",
    "benefits.core.context_processors.authentication",
    "benefits.core.context_processors.recaptcha",
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
        "NAME": "django.db",
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

# OAuth configuration

OAUTH_AUTHORITY = os.environ.get("DJANGO_OAUTH_AUTHORITY", "http://example.com")
OAUTH_CLIENT_NAME = os.environ.get("DJANGO_OAUTH_CLIENT_NAME", "benefits-oauth-client-name")
OAUTH_CLIENT_ID = os.environ.get("DJANGO_OAUTH_CLIENT_ID", "benefits-oauth-client-id")

if OAUTH_CLIENT_NAME:
    AUTHLIB_OAUTH_CLIENTS = {
        OAUTH_CLIENT_NAME: {
            "client_id": OAUTH_CLIENT_ID,
            "server_metadata_url": f"{OAUTH_AUTHORITY}/.well-known/openid-configuration",
            "client_kwargs": {"code_challenge_method": "S256", "scope": "openid"},
        }
    }

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

# rate limit configuration

# number of requests allowed in the given period
RATE_LIMIT = int(os.environ.get("DJANGO_RATE_LIMIT", 5))

# HTTP request methods to rate limit
RATE_LIMIT_METHODS = os.environ.get("DJANGO_RATE_LIMIT_METHODS", "POST").upper().split(",")

# number of seconds before additional requests are denied
RATE_LIMIT_PERIOD = int(os.environ.get("DJANGO_RATE_LIMIT_PERIOD", 60))

# Rate Limit feature flag
RATE_LIMIT_ENABLED = all((RATE_LIMIT > 0, len(RATE_LIMIT_METHODS) > 0, RATE_LIMIT_PERIOD > 0))

# reCAPTCHA configuration

RECAPTCHA_API_URL = os.environ.get("DJANGO_RECAPTCHA_API_URL", "https://www.google.com/recaptcha/api.js")
RECAPTCHA_SITE_KEY = os.environ.get("DJANGO_RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.environ.get("DJANGO_RECAPTCHA_SECRET_KEY")
RECAPTCHA_VERIFY_URL = os.environ.get("DJANGO_RECAPTCHA_VERIFY_URL", "https://www.google.com/recaptcha/api/siteverify")
RECAPTCHA_ENABLED = all((RECAPTCHA_API_URL, RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY, RECAPTCHA_VERIFY_URL))

# Content Security Policy
# Configuration docs at https://django-csp.readthedocs.io/en/latest/configuration.html

# In particular, note that the inner single-quotes are required!
# https://django-csp.readthedocs.io/en/latest/configuration.html#policy-settings

CSP_DEFAULT_SRC = ["'self'"]

CSP_CONNECT_SRC = ["'self'", "https://api.amplitude.com/"]
env_connect_src = _filter_empty(os.environ.get("DJANGO_CSP_CONNECT_SRC", "").split(","))
CSP_CONNECT_SRC.extend(env_connect_src)

CSP_FONT_SRC = ["'self'", "https://california.azureedge.net/cdt/statetemplate/", "https://fonts.gstatic.com/"]
env_font_src = _filter_empty(os.environ.get("DJANGO_CSP_FONT_SRC", "").split(","))
CSP_FONT_SRC.extend(env_font_src)

CSP_FRAME_ANCESTORS = ["'none'"]

CSP_FRAME_SRC = ["'none'"]
env_frame_src = _filter_empty(os.environ.get("DJANGO_CSP_FRAME_SRC", "").split(","))
CSP_FRAME_SRC.extend(env_frame_src)
if RECAPTCHA_ENABLED:
    CSP_FRAME_SRC.append("https://www.google.com")


CSP_SCRIPT_SRC = [
    "'unsafe-inline'",
    "https://california.azureedge.net/cdt/statetemplate/",
    "https://cdn.amplitude.com/libs/",
    "https://code.jquery.com/",
    "*.littlepay.com",
]
env_script_src = _filter_empty(os.environ.get("DJANGO_CSP_SCRIPT_SRC", "").split(","))
CSP_SCRIPT_SRC.extend(env_script_src)
if RECAPTCHA_ENABLED:
    CSP_SCRIPT_SRC.extend(["https://www.google.com/recaptcha/", "https://www.gstatic.com/recaptcha/releases/"])

CSP_STYLE_SRC = [
    "'self'",
    "'unsafe-inline'",
    "https://california.azureedge.net/cdt/statetemplate/",
    "https://fonts.googleapis.com/css",
]
env_style_src = _filter_empty(os.environ.get("DJANGO_CSP_STYLE_SRC", "").split(","))
CSP_STYLE_SRC.extend(env_style_src)
