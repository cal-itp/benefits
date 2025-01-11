import os

from playwright.sync_api import Page, expect
import pyotp

from models import Index


def test_older_adult_flow(page: Page):
    page.goto("/")

    index = Index(page)
    eligibility_index = index.select_agency("California State Transit")
    eligibility_start = eligibility_index.select_flow("Older Adult")

    login_gov = eligibility_start.get_started_with_login_gov()

    username = os.environ.get("PLAYWRIGHT_LOGIN_GOV_OLDER_ADULT_USERNAME")
    password = os.environ.get("PLAYWRIGHT_LOGIN_GOV_OLDER_ADULT_PASSWORD")
    login_gov.sign_in(username, password)

    authenticator_secret = os.environ.get("PLAYWRIGHT_LOGIN_GOV_OLDER_ADULT_AUTHENTICATOR_SECRET")
    # create instance of "authenticator app"
    totp = pyotp.TOTP(authenticator_secret)
    enrollment_index = login_gov.enter_otp(totp.now())

    enrollment_index.enroll("Test User", "4111 1111 1111 1111", "12/34", "123")

    # enrollment can take a bit
    page.wait_for_timeout(10000)

    success_message = page.get_by_text("You can now use your contactless card to tap to ride with a reduced fare!")
    expect(success_message).to_be_visible()


def test_us_veteran_flow(page: Page):
    page.goto("/")

    # Index - select transit agency
    page.get_by_role("link", name="Choose your Provider").click()
    page.get_by_role("link", name="California State Transit").click()

    # Eligibility Index - select enrollment flow
    page.get_by_label("U.S. Veteran").check()
    page.wait_for_load_state("networkidle")  # wait for reCAPTCHA to finish loading
    page.get_by_role("button", name="Choose this benefit").click()

    # Eligibility Start - continue to Login.gov
    page.get_by_role("link", name="Get started with Login.gov").click()

    # sign in to Login.gov
    page.get_by_label("Email address").click()
    username = os.environ.get("PLAYWRIGHT_LOGIN_GOV_VETERAN_USERNAME")
    page.get_by_label("Email address").fill(username)
    page.get_by_label("Email address").press("Tab")

    password = os.environ.get("PLAYWRIGHT_LOGIN_GOV_VETERAN_PASSWORD")
    page.get_by_label("Password", exact=True).fill(password)

    page.get_by_role("button", name="Sign in").click()

    # one-time password
    # create instance of "authenticator app"
    authenticator_secret = os.environ.get("PLAYWRIGHT_LOGIN_GOV_VETERAN_AUTHENTICATOR_SECRET")
    totp = pyotp.TOTP(authenticator_secret)
    page.get_by_label("One-time code").click()
    page.get_by_label("One-time code").fill(totp.now())

    page.get_by_role("button", name="Submit").click()

    # Enrollment Index - fill out transit processor form in pop-up window
    with page.expect_popup() as popup_info:
        page.get_by_role("button", name="Enroll").click()

    popup = popup_info.value
    popup.wait_for_timeout(3000)

    popup.get_by_text("Cardholder name").click()

    cardholder_name = "Test User"
    popup.get_by_label("Cardholder name").fill(cardholder_name)
    popup.keyboard.press("Tab")

    card_number = "4111 1111 1111 1111"
    popup.get_by_label("Card number").fill(card_number)
    popup.keyboard.press("Tab")

    expiration = "12/34"
    popup.get_by_label("mm/yy").fill(expiration)
    popup.keyboard.press("Tab")

    security_code = "123"
    popup.get_by_text("Security code", exact=True).click()
    popup.get_by_label("Security code").fill(security_code)

    # trigger form validation - not sure why their form behaves this way
    popup.keyboard.press("Shift+Tab")
    popup.keyboard.press("Shift+Tab")
    popup.keyboard.press("Shift+Tab")
    popup.keyboard.press("Tab")

    popup.get_by_role("group", name="Enter your card details").get_by_role("button").click()

    page.wait_for_timeout(10000)

    success_message = page.get_by_text("You can now use your contactless card to tap to ride with a reduced fare!")
    expect(success_message).to_be_visible()


def test_calfresh_cardholder_flow(page: Page):
    page.goto("/")

    # Index - select transit agency
    page.get_by_role("link", name="Choose your Provider").click()
    page.get_by_role("link", name="California State Transit").click()

    # Eligibility Index - select enrollment flow
    page.get_by_label("CalFresh Cardholder").check()
    page.wait_for_load_state("networkidle")  # wait for reCAPTCHA to finish loading
    page.get_by_role("button", name="Choose this benefit").click()

    # Eligibility Start - continue to Login.gov
    page.get_by_role("link", name="Get started with Login.gov").click()

    # sign in to Login.gov
    page.get_by_label("Email address").click()
    username = os.environ.get("PLAYWRIGHT_LOGIN_GOV_CALFRESH_USERNAME")
    page.get_by_label("Email address").fill(username)
    page.get_by_label("Email address").press("Tab")

    password = os.environ.get("PLAYWRIGHT_LOGIN_GOV_CALFRESH_PASSWORD")
    page.get_by_label("Password", exact=True).fill(password)

    page.get_by_role("button", name="Sign in").click()

    # one-time password
    # create instance of "authenticator app"
    authenticator_secret = os.environ.get("PLAYWRIGHT_LOGIN_GOV_CALFRESH_AUTHENTICATOR_SECRET")
    totp = pyotp.TOTP(authenticator_secret)
    page.get_by_label("One-time code").click()
    page.get_by_label("One-time code").fill(totp.now())

    page.get_by_role("button", name="Submit").click()

    # Enrollment Index - fill out transit processor form in pop-up window
    with page.expect_popup() as popup_info:
        page.get_by_role("button", name="Enroll").click()

    popup = popup_info.value
    popup.wait_for_timeout(3000)

    popup.get_by_text("Cardholder name").click()

    cardholder_name = "Test User"
    popup.get_by_label("Cardholder name").fill(cardholder_name)
    popup.keyboard.press("Tab")

    card_number = "4111 1111 1111 1111"
    popup.get_by_label("Card number").fill(card_number)
    popup.keyboard.press("Tab")

    expiration = "12/34"
    popup.get_by_label("mm/yy").fill(expiration)
    popup.keyboard.press("Tab")

    security_code = "123"
    popup.get_by_text("Security code", exact=True).click()
    popup.get_by_label("Security code").fill(security_code)

    # trigger form validation - not sure why their form behaves this way
    popup.keyboard.press("Shift+Tab")
    popup.keyboard.press("Shift+Tab")
    popup.keyboard.press("Shift+Tab")
    popup.keyboard.press("Tab")

    popup.get_by_role("group", name="Enter your card details").get_by_role("button").click()

    page.wait_for_timeout(10000)

    reenrollment_error_message = page.get_by_text("You are still enrolled in this benefit")
    expect(reenrollment_error_message).to_be_visible()
