from playwright.sync_api import BrowserContext, expect

from .models import Index


def test_agency_card_flow(context: BrowserContext, base_url, agency_card_flows, valid_payment_card):
    for agency_flow, cred in agency_card_flows:
        print(agency_flow)

        page = context.new_page()

        page.goto(base_url)

        index = Index(page)
        eligibility_index = index.select_agency(agency_flow.agency)
        eligibility_start = eligibility_index.select_flow(agency_flow.flow)
        eligibility_confirm = eligibility_start.click_continue()
        enrollment_index = eligibility_confirm.submit_form(cred.sub, cred.name)
        enrollment_index.enroll(valid_payment_card)

        # enrollment can take a bit
        page.wait_for_timeout(15000)

        success_message = page.get_by_text("You can now use your contactless card to tap to ride with a reduced fare!")
        expect(success_message).to_be_visible()
