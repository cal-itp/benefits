"""
Django settings for benefits project.
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ADMIN = os.environ.get("DJANGO_ADMIN", "False").lower() == "true"

ALLOWED_HOSTS = []

if DEBUG:
    ALLOWED_HOSTS.extend(["*"])
else:
    hosts = os.environ["DJANGO_ALLOWED_HOSTS"].split()
    ALLOWED_HOSTS.extend(hosts)

# Application definition

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "benefits.core",
    "benefits.discounts",
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
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "benefits.core.middleware.DebugSession",
]

if ADMIN:
    MIDDLEWARE.extend(
        [
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ]
    )

CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_AGE = 3600
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

ROOT_URLCONF = "benefits.urls"

template_ctx_processors = [
    "django.template.context_processors.request",
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

LANGUAGES = [("en", "English"), ("es", "Español")]

LOCALE_PATHS = [os.path.join(BASE_DIR, "benefits", "locale")]

USE_I18N = True
USE_L10N = True

TIME_ZONE = "UTC"
USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "benefits", "static")]
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
