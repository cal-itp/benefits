import re
from playwright.sync_api import Page, expect


def test_has_title(page: Page):
    page.goto("https://dev-benefits.calitp.org/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Cal-ITP"))


def test_get_started_link(page: Page):
    page.goto("https://dev-benefits.calitp.org/")

    # Click the Choose your provider link.
    page.get_by_text("Choose your provider").click()

    page.get_by_text("California State Transit (dev)").click()

    page.get_by_label("Medicare Cardholder").click()

    page.get_by_text("Choose this benefit").click()

    page.get_by_text("Continue to Medicare.gov").click()

    page.wait_for_timeout(5000)

    # # Expects page to have a heading with the name of Installation.
    # expect(page.get("heading", name="Installation")).to_be_visible()
