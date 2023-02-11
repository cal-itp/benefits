from benefits import VERSION
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import os


def configure():
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    if SENTRY_DSN:
        print("Enabling Sentry…")

        SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "local")

        # https://docs.sentry.io/platforms/python/configuration/
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
            ],
            traces_sample_rate=1.0,
            environment=SENTRY_ENVIRONMENT,
            release=VERSION,
        )
    else:
        print("SENTRY_DSN not set, so won't send events")
