from playwright.sync_api import BrowserContext, expect

from models import Index


def test_agency_card_flow(context: BrowserContext, base_url):
    page = context.new_page()

    page.goto(base_url)

    index = Index(page)
    eligibility_index = index.select_agency("California State Transit")
    eligibility_start = eligibility_index.select_flow("Agency Cardholder")
    eligibility_confirm = eligibility_start.click_continue()
    enrollment_index = eligibility_confirm.submit_form("71162", "Box")
    enrollment_index.enroll("Test User", "4111 1111 1111 1111", "12/34", "123")

    # enrollment can take a bit
    page.wait_for_timeout(10000)

    success_message = page.get_by_text("You can now use your contactless card to tap to ride with a reduced fare!")
    expect(success_message).to_be_visible()
