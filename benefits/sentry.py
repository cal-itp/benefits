import logging
import shutil
import os
import subprocess

from django.conf import settings
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.scrubber import EventScrubber, DEFAULT_DENYLIST

from benefits import VERSION

logger = logging.getLogger(__name__)

SENTRY_CSP_REPORT_URI = None


def git_available():
    return bool(shutil.which("git"))


# https://stackoverflow.com/a/24584384/358804
def is_git_directory(path="."):
    with open(os.devnull, "w") as dev_null:
        return subprocess.call(["git", "-C", path, "status"], stderr=dev_null, stdout=dev_null) == 0


# https://stackoverflow.com/a/21901260/358804
def get_git_revision_hash():
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()


def get_sha_file_path():
    current_file = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_file, "..", "static", "sha.txt")


def get_sha_from_file():
    sha_path = get_sha_file_path()
    if os.path.isfile(sha_path):
        with open(sha_path) as f:
            return f.read().strip()
    else:
        return None


def get_release() -> str:
    """Returns the first available: the SHA from Git, the value from sha.txt, or the VERSION."""

    if git_available() and is_git_directory():
        return get_git_revision_hash()
    else:
        sha = get_sha_from_file()
        if sha:
            return sha
        else:
            # one of the above *should* always be available, but including this just in case
            return VERSION


def get_denylist():
    # custom denylist
    denylist = DEFAULT_DENYLIST + ["sub", "name"]
    return denylist


def get_traces_sample_rate():
    try:
        rate = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.0"))
        if rate < 0.0 or rate > 1.0:
            logger.warning("SENTRY_TRACES_SAMPLE_RATE was not in the range [0.0, 1.0], defaulting to 0.0")
            rate = 0.0
        else:
            logger.info(f"SENTRY_TRACES_SAMPLE_RATE set to: {rate}")
    except ValueError:
        logger.warning("SENTRY_TRACES_SAMPLE_RATE did not parse to float, defaulting to 0.0")
        rate = 0.0

    return rate


def configure():
    sentry_dsn = os.environ.get("SENTRY_DSN")
    sentry_environment = os.environ.get("SENTRY_ENVIRONMENT", settings.RUNTIME_ENVIRONMENT())

    if sentry_dsn:
        release = get_release()
        logger.info(f"Enabling Sentry for environment '{sentry_environment}', release '{release}'...")

        # https://docs.sentry.io/platforms/python/configuration/
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                DjangoIntegration(),
            ],
            traces_sample_rate=get_traces_sample_rate(),
            environment=sentry_environment,
            release=release,
            in_app_include=["benefits"],
            # send_default_pii must be False (the default) for a custom EventScrubber/denylist
            # https://docs.sentry.io/platforms/python/data-management/sensitive-data/#event_scrubber
            send_default_pii=False,
            event_scrubber=EventScrubber(denylist=get_denylist(), recursive=True),
        )

        # override the module-level variable when configuration happens, if set
        global SENTRY_CSP_REPORT_URI
        SENTRY_CSP_REPORT_URI = os.environ.get("SENTRY_REPORT_URI", "")
    else:
        logger.info("SENTRY_DSN not set, so won't send events")
