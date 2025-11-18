"""
Django settings for benefits project.
"""

import os

from django.conf import settings

from csp.constants import NONCE, NONE, SELF, UNSAFE_INLINE

from benefits import sentry


def _filter_empty(ls):
    return [s for s in ls if s]


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = _filter_empty(os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(","))


class RUNTIME_ENVS:
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


def RUNTIME_ENVIRONMENT():
    """Helper calculates the current runtime environment from ALLOWED_HOSTS."""

    # usage of django.conf.settings.ALLOWED_HOSTS here (rather than the module variable directly)
    # is to ensure dynamic calculation, e.g. for unit tests and elsewhere this setting is needed
    env = RUNTIME_ENVS.LOCAL
    if "dev-benefits.calitp.org" in settings.ALLOWED_HOSTS:
        env = RUNTIME_ENVS.DEV
    elif "test-benefits.calitp.org" in settings.ALLOWED_HOSTS:
        env = RUNTIME_ENVS.TEST
    elif "benefits.calitp.org" in settings.ALLOWED_HOSTS:
        env = RUNTIME_ENVS.PROD
    return env


# Application definition

INSTALLED_APPS = [
    "benefits.apps.BenefitsAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "csp",
    "adminsortable2",
    "cdt_identity",
    "django_google_sso",
    "benefits.core",
    "benefits.enrollment",
    "benefits.enrollment_littlepay",
    "benefits.enrollment_switchio",
    "benefits.eligibility",
    "benefits.oauth",
    "benefits.in_person",
]

GOOGLE_SSO_CLIENT_ID = os.environ.get("GOOGLE_SSO_CLIENT_ID", "secret")
GOOGLE_SSO_PROJECT_ID = os.environ.get("GOOGLE_SSO_PROJECT_ID", "benefits-admin")
GOOGLE_SSO_CLIENT_SECRET = os.environ.get("GOOGLE_SSO_CLIENT_SECRET", "secret")
GOOGLE_SSO_ALLOWABLE_DOMAINS = _filter_empty(os.environ.get("GOOGLE_SSO_ALLOWABLE_DOMAINS", "compiler.la").split(","))
GOOGLE_SSO_STAFF_LIST = _filter_empty(os.environ.get("GOOGLE_SSO_STAFF_LIST", "").split(","))
GOOGLE_SSO_SUPERUSER_LIST = _filter_empty(os.environ.get("GOOGLE_SSO_SUPERUSER_LIST", "").split(","))
GOOGLE_SSO_LOGO_URL = "/static/img/icon/google_sso_logo.svg"
GOOGLE_SSO_TEXT = "Log in with Google"
GOOGLE_SSO_SAVE_ACCESS_TOKEN = True
GOOGLE_SSO_PRE_LOGIN_CALLBACK = "benefits.core.admin.pre_login_user"
GOOGLE_SSO_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
SSO_SHOW_FORM_ON_ADMIN_PAGE = os.environ.get("SSO_SHOW_FORM_ON_ADMIN_PAGE", "False").lower() == "true"
STAFF_GROUP_NAME = "Cal-ITP"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "benefits.core.middleware.Healthcheck",
    "benefits.core.middleware.HealthcheckUserAgents",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "benefits.core.middleware.ChangedLanguageEvent",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

if DEBUG:
    MIDDLEWARE.append("benefits.core.middleware.DebugSession")

HEALTHCHECK_USER_AGENTS = _filter_empty(os.environ.get("HEALTHCHECK_USER_AGENTS", "").split(","))

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

# required so that cross-origin pop-ups (like the enrollment overlay) have access to parent window context
# https://github.com/cal-itp/benefits/pull/793
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

# the NGINX reverse proxy sits in front of the application in deployed environments
# SSL terminates before getting to Django, and NGINX adds this header to indicate
# if the original request was secure or not
#
# See https://docs.djangoproject.com/en/5.0/ref/settings/#secure-proxy-ssl-header
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ROOT_URLCONF = "benefits.urls"

template_ctx_processors = [
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "benefits.core.context_processors.agency",
    "benefits.core.context_processors.active_agencies",
    "benefits.core.context_processors.analytics",
    "benefits.core.context_processors.authentication",
    "benefits.core.context_processors.enrollment",
    "benefits.core.context_processors.origin",
    "benefits.core.context_processors.routes",
    "benefits.core.context_processors.feature_flags",
]

if DEBUG:
    template_ctx_processors.extend(
        [
            "django.template.context_processors.debug",
            "benefits.core.context_processors.debug",
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

STORAGE_DIR = os.environ.get("DJANGO_STORAGE_DIR", BASE_DIR)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(STORAGE_DIR, os.environ.get("DJANGO_DB_FILE", "django.db")),
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
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


# Internationalization

LANGUAGE_CODE = "en"

LANGUAGE_COOKIE_HTTPONLY = True
# `Lax` allows the cookie to travel with the user and be sent back to Benefits
# during redirection e.g. through IdG/Login.gov or a Transit Processor portal
# ensuring the app is displayed in the same language
LANGUAGE_COOKIE_SAMESITE = "Lax"
LANGUAGE_COOKIE_SECURE = True

LANGUAGES = [("en", "English"), ("es", "Español")]

LOCALE_PATHS = [os.path.join(BASE_DIR, "benefits", "locale")]

USE_I18N = True

# See https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-TIME_ZONE
# > Note that this isn’t necessarily the time zone of the server.
# > When USE_TZ is True, this is the default time zone that Django will use to display datetimes in templates
# > and to interpret datetimes entered in forms.
TIME_ZONE = "America/Los_Angeles"
USE_TZ = True

# https://docs.djangoproject.com/en/5.0/topics/i18n/formatting/#creating-custom-format-files
FORMAT_MODULE_PATH = [
    "benefits.locale",
]

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "benefits", "static")]
# use Manifest Static Files Storage by default
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": os.environ.get(
            "DJANGO_STATICFILES_STORAGE", "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        )
    },
}
STATIC_ROOT = os.path.join(BASE_DIR, "static")

#  User-uploaded files

MEDIA_ROOT = os.path.join(STORAGE_DIR, "uploads/")

MEDIA_URL = "/media/"

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
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

sentry.configure()

# Analytics configuration

ANALYTICS_KEY = os.environ.get("ANALYTICS_KEY")

# reCAPTCHA configuration

RECAPTCHA_API_URL = os.environ.get("DJANGO_RECAPTCHA_API_URL", "https://www.google.com/recaptcha/api.js")
RECAPTCHA_SITE_KEY = os.environ.get("DJANGO_RECAPTCHA_SITE_KEY")
RECAPTCHA_API_KEY_URL = f"{RECAPTCHA_API_URL}?render={RECAPTCHA_SITE_KEY}"
RECAPTCHA_SECRET_KEY = os.environ.get("DJANGO_RECAPTCHA_SECRET_KEY")
RECAPTCHA_VERIFY_URL = os.environ.get("DJANGO_RECAPTCHA_VERIFY_URL", "https://www.google.com/recaptcha/api/siteverify")
RECAPTCHA_ENABLED = all((RECAPTCHA_API_URL, RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY, RECAPTCHA_VERIFY_URL))

# Content Security Policy
# Configuration docs at https://django-csp.readthedocs.io/en/latest/configuration.html+

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "base-uri": [NONE],
        "connect-src": [SELF, "https://api.amplitude.com/"],
        "default-src": [SELF],
        "font-src": [SELF, "https://fonts.gstatic.com/"],
        "frame-ancestors": [NONE],
        "frame-src": ["*.littlepay.com"],
        "img-src": [SELF, "data:", "*.googleusercontent.com"],
        "object-src": [NONE],
        "script-src": [
            SELF,
            "https://cdn.amplitude.com/libs/",
            "https://cdn.jsdelivr.net/",
            "*.littlepay.com",
            "https://code.jquery.com/jquery-3.6.0.min.js",
            NONCE,  # https://django-csp.readthedocs.io/en/latest/nonce.html
        ],
        "style-src": [
            SELF,
            UNSAFE_INLINE,
            "https://fonts.googleapis.com/css",
            "https://fonts.googleapis.com/css2",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/",
        ],
    }
}

# connect-src additions
env_connect_src = _filter_empty(os.environ.get("DJANGO_CSP_CONNECT_SRC", "").split(","))
if RECAPTCHA_ENABLED:
    env_connect_src.append("https://www.google.com/recaptcha/")
CONTENT_SECURITY_POLICY["DIRECTIVES"]["connect-src"].extend(env_connect_src)

# font-src additions
env_font_src = _filter_empty(os.environ.get("DJANGO_CSP_FONT_SRC", "").split(","))
CONTENT_SECURITY_POLICY["DIRECTIVES"]["font-src"].extend(env_font_src)

# frame-src additions
env_frame_src = _filter_empty(os.environ.get("DJANGO_CSP_FRAME_SRC", "").split(","))
if RECAPTCHA_ENABLED:
    env_frame_src.append("https://www.google.com")
CONTENT_SECURITY_POLICY["DIRECTIVES"]["frame-src"].extend(env_frame_src)

# script-src additions
env_script_src = _filter_empty(os.environ.get("DJANGO_CSP_SCRIPT_SRC", "").split(","))
if RECAPTCHA_ENABLED:
    env_script_src.extend(["https://www.google.com/recaptcha/", "https://www.gstatic.com/recaptcha/releases/"])
CONTENT_SECURITY_POLICY["DIRECTIVES"]["script-src"].extend(env_script_src)

# style-src additions
env_style_src = _filter_empty(os.environ.get("DJANGO_CSP_STYLE_SRC", "").split(","))
CONTENT_SECURITY_POLICY["DIRECTIVES"]["style-src"].extend(env_style_src)

# adjust report-uri when using Sentry
if sentry.SENTRY_CSP_REPORT_URI:
    CONTENT_SECURITY_POLICY["DIRECTIVES"]["report-uri"] = sentry.SENTRY_CSP_REPORT_URI


# Configuration for requests
# https://requests.readthedocs.io/en/latest/user/advanced/#timeouts

try:
    REQUESTS_CONNECT_TIMEOUT = int(os.environ.get("REQUESTS_CONNECT_TIMEOUT"))
except Exception:
    REQUESTS_CONNECT_TIMEOUT = 3

try:
    REQUESTS_READ_TIMEOUT = int(os.environ.get("REQUESTS_READ_TIMEOUT"))
except Exception:
    REQUESTS_READ_TIMEOUT = 20

REQUESTS_TIMEOUT = (REQUESTS_CONNECT_TIMEOUT, REQUESTS_READ_TIMEOUT)

# Email
# https://docs.djangoproject.com/en/5.2/ref/settings/#email-backend
# https://github.com/retech-us/django-azure-communication-email
AZURE_COMMUNICATION_CONNECTION_STRING = os.environ.get("AZURE_COMMUNICATION_CONNECTION_STRING")

if AZURE_COMMUNICATION_CONNECTION_STRING:
    EMAIL_BACKEND = "django_azure_communication_email.EmailBackend"
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = os.path.join(STORAGE_DIR, ".sent_emails")

# https://docs.djangoproject.com/en/5.2/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.calitp.org")
