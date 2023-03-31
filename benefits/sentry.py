import shutil
import os
import subprocess

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.scrubber import EventScrubber, DEFAULT_DENYLIST

from benefits import VERSION


SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "local")


def git_available():
    return bool(shutil.which("git"))


# https://stackoverflow.com/a/24584384/358804
def is_git_directory(path="."):
    dev_null = open(os.devnull, "w")
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


def configure():
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    if SENTRY_DSN:
        release = get_release()
        print(f"Enabling Sentry for environment '{SENTRY_ENVIRONMENT}', release '{release}'...")

        # https://docs.sentry.io/platforms/python/configuration/
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
            ],
            traces_sample_rate=1.0,
            environment=SENTRY_ENVIRONMENT,
            release=release,
            in_app_include=["benefits"],
            # https://docs.sentry.io/platforms/python/data-management/sensitive-data/#event_scrubber
            send_default_pii=False,
            event_scrubber=EventScrubber(denylist=get_denylist()),
        )
    else:
        print("SENTRY_DSN not set, so won't send events")
