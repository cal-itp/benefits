"""
Tests that use requests to call the MOBILEvario API.
"""

import json
import logging
import os
from dataclasses import dataclass
from enum import Enum

import pytest
from playwright.sync_api import Dialog, Page, expect

logger = logging.getLogger(__name__)

PSTA_INIT_ENROLLMENT_API_BASE_URL = os.environ.get("psta_init_enrollment_api_base_url")
PSTA_INIT_ENROLLMENT_API_AUTHORIZATION_HEADER = os.environ.get("psta_init_enrollment_api_authorization_header")


def endpoint_url(endpoint):
    return f"{PSTA_INIT_ENROLLMENT_API_BASE_URL}/api/{endpoint}"


class Endpoints(Enum):
    TransitAccounts = endpoint_url("TransitAccounts")


@dataclass
class CardDetails:
    card_number: str
    expiration_date: str
    cvv: str


def generate_month_year_codes():
    dates = []
    for year in range(2026, 2027):
        for month in range(1, 13):
            if not (year == 2026 and month < 8):
                dates.append(f"{month:02d} / {str(year)[-2:]}")
    return dates


def generate_3digit_codes():
    return [f"{i:03d}" for i in range(411, 501)]


def my_params():
    card_numbers = ["4111 1111 1111 1111", "4242 4242 4242 4242"]
    expiration_dates = generate_month_year_codes()
    cvvs = generate_3digit_codes()

    card_details = []
    for c in card_numbers:
        for e in expiration_dates:
            for cv in cvvs:
                card_details.append(CardDetails(c, e, cv))
    return card_details


TEST_CASES = my_params()


@pytest.mark.parametrize("card_details", TEST_CASES, ids=lambda tc: tc)
def test_get_TransitAccount(page: Page, card_details: CardDetails):
    page.context.set_extra_http_headers(
        {
            "Authorization": PSTA_INIT_ENROLLMENT_API_AUTHORIZATION_HEADER,
        }
    )

    page.goto("https://benefits-4000--cal-itp-previews.netlify.app/init-research/collectjs-demo.html")

    def handle_card_token(dialog: Dialog):
        message_json = json.loads(dialog.message)
        token = message_json["token"]
        dialog.accept()

        page.goto(Endpoints.TransitAccounts.value + f"?BankingServiceToken={token}")

    page.on("dialog", lambda dialog: handle_card_token(dialog))

    # page.wait_for_timeout(1500)  # need to wait for the iframes to load
    card_number_input = page.locator("#CollectJSInlineccnumber").content_frame.get_by_role("textbox", name="Card Number")
    card_number_input.type(card_details.card_number)

    expiration_date_input = page.locator("#CollectJSInlineccexp").content_frame.get_by_role("textbox", name="Card Expiration")
    expiration_date_input.type(card_details.expiration_date)

    security_code_input = page.locator("#CollectJSInlinecvv").content_frame.get_by_role("textbox", name="CVV Code")
    security_code_input.type(card_details.cvv)

    pay_button = page.get_by_role("button", name="Pay")
    pay_button.click()

    page.wait_for_timeout(3000)

    expect(page.get_by_text('{"TotalCount":0,"Result":[]}')).not_to_be_visible()
