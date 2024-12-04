from playwright.sync_api import Page, expect
import pytest


@pytest.mark.dev
@pytest.mark.test
@pytest.mark.prod
def test_healthcheck(page: Page):
    page.goto("/healthcheck")

    expect(page.get_by_text("Healthy")).to_be_visible()
