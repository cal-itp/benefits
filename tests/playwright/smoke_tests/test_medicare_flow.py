import os
from playwright.sync_api import Page, expect

from models import Index


def test_medicare_cardholder_flow(page: Page):
    page.goto("/")

    index = Index(page)
    eligibility_index = index.select_agency("California State Transit")
    eligibility_start = eligibility_index.select_flow("Medicare Cardholder")

    # avoid looking like a bot
    page.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")

    medicare_gov = eligibility_start.continue_to_medicare_gov()

    username = os.environ.get("PLAYWRIGHT_MEDICARE_GOV_USERNAME")
    password = os.environ.get("PLAYWRIGHT_MEDICARE_GOV_PASSWORD")
    medicare_gov.log_in(username, password)
    enrollment_index = medicare_gov.accept_consent_screen()

    enrollment_index.enroll("Test User", "4111 1111 1111 1111", "12/34", "123")

    # enrollment can take a bit
    page.wait_for_timeout(10000)

    success_message = page.get_by_text("You can now use your contactless card to tap to ride with a reduced fare!")
    expect(success_message).to_be_visible()
