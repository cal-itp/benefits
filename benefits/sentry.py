from benefits import VERSION
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import os
import subprocess


SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "local")


# https://stackoverflow.com/a/21901260/358804
def get_git_revision_hash():
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()


def get_sha_path():
    current_file = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_file, "..", "static", "sha.txt")


def get_release() -> str:
    """On 'local' and 'dev', returns the Git SHA. Otherwise, returns the VERSION."""

    sha_path = get_sha_path()
    if SENTRY_ENVIRONMENT == "local":
        return get_git_revision_hash()
    elif SENTRY_ENVIRONMENT == "dev" and os.path.isfile(sha_path):
        with open(sha_path) as f:
            return f.read().strip()
    else:
        return VERSION


def configure():
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    if SENTRY_DSN:
        print("Enabling Sentry…")

        # https://docs.sentry.io/platforms/python/configuration/
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
            ],
            traces_sample_rate=1.0,
            environment=SENTRY_ENVIRONMENT,
            release=get_release(),
        )
    else:
        print("SENTRY_DSN not set, so won't send events")
