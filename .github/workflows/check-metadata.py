from datetime import datetime, timezone
from functools import cache
import json
from pathlib import Path
import sys

import requests


def get_agency_url(agency: str):
    path = Path("./metadata.json")
    if not path.exists():
        raise RuntimeError("Metadata file not found")

    config = json.loads(path.read_text())
    return config[agency]


@cache
def get_metadata(url: str):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def check_metadata_timestamp(url: str):
    now = datetime.now(tz=timezone.utc)
    data = get_metadata(url)
    ts = data["db"]["timestamp"]
    timestamp = datetime.fromisoformat(ts)

    if not all((timestamp.year == now.year, timestamp.month == now.month, timestamp.day == now.day)):
        raise RuntimeError(f"Database timestamp mismatch: {ts}")


def check_metadata_users(url: str):
    data = get_metadata(url)
    users = data["db"]["users"]

    if users < 1:
        raise RuntimeError("Database has no users")


def check_metadata_eligibility(url: str):
    data = get_metadata(url)
    eligibility = data["db"]["eligibility"]

    if len(eligibility) < 1:
        raise RuntimeError("Database has no eligibility")


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        raise RuntimeError("Usage: check-metadata AGENCY")

    agency = args[1]
    url = get_agency_url(agency)
    check_metadata_timestamp(url)
    check_metadata_users(url)
    check_metadata_eligibility(url)
