"""
Tests that use requests to call the MOBILEvario API.
"""

import os
from enum import StrEnum

import pytest
import requests

PSTA_INIT_ENROLLMENT_API_BASE_URL = os.environ.get("psta_init_enrollment_api_base_url")
PSTA_INIT_ENROLLMENT_API_AUTHORIZATION_HEADER = os.environ.get("psta_init_enrollment_api_authorization_header")


def endpoint_url(endpoint):
    return f"{PSTA_INIT_ENROLLMENT_API_BASE_URL}/api/{endpoint}"


class Endpoints(StrEnum):
    TransitAccounts = endpoint_url("TransitAccounts")


@pytest.mark.enable_socket
def test_get_TransitAccount():
    # paste a list of card tokens for which to get TransitAccounts here
    card_tokens = []

    for token in card_tokens:
        response = requests.get(
            Endpoints.TransitAccounts,
            params={
                "IsBlocked": "false",
                "BankingServiceToken": token,
            },
            headers={"Authorization": PSTA_INIT_ENROLLMENT_API_AUTHORIZATION_HEADER},
            timeout=0,
        )

        response.raise_for_status()

        results = response.json()["Result"]

        print(f"## Trying token {token}")

        if len(results) > 0:
            print("We found a TransitAccount! (see below)")
            print("")
            print(results)
        else:
            print(f"Token {token} does not have a TransitAccount associated with it.")
