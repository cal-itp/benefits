import os

from playwright.sync_api import Page, expect


def test_medicare_cardholder_flow(page: Page):
    page.goto("/")
    page.click("text='Choose your Provider'")
    page.get_by_role("link", name="California State Transit (dev)").click()
    page.get_by_label("Medicare Cardholder You must").check()
    page.get_by_role("button", name="Choose this benefit").click()
    page.get_by_role("button", name="Continue to Medicare.gov").click()
    page.get_by_label("Username", exact=True).click()

    username = os.environ.get("MEDICARE_FLOW_USERNAME")
    page.get_by_label("Username", exact=True).fill(username)

    password = os.environ.get("MEDICARE_FLOW_PASSWORD")
    page.get_by_label("Password").fill(password)

    page.get_by_role("button", name="Log in").click()

    expect
