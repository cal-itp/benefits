from playwright.sync_api import Page, expect


def test_dev_healthcheck(page: Page):
    page.goto("https://dev-benefits.calitp.org/healthcheck")

    expect(page.get_by_text("Healthy")).to_be_visible()
