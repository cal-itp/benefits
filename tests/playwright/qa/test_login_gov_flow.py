import os

from playwright.sync_api import BrowserContext, expect
import pyotp

from models import Index


def test_older_adult_flow(context: BrowserContext, base_url):
    page = context.new_page()

    page.goto(base_url)

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


def test_us_veteran_flow(context: BrowserContext, base_url):
    page = context.new_page()

    page.goto(base_url)

    index = Index(page)
    eligibility_index = index.select_agency("California State Transit")
    eligibility_start = eligibility_index.select_flow("U.S. Veteran")

    login_gov = eligibility_start.get_started_with_login_gov()

    username = os.environ.get("PLAYWRIGHT_LOGIN_GOV_VETERAN_USERNAME")
    password = os.environ.get("PLAYWRIGHT_LOGIN_GOV_VETERAN_PASSWORD")
    login_gov.sign_in(username, password)

    authenticator_secret = os.environ.get("PLAYWRIGHT_LOGIN_GOV_VETERAN_AUTHENTICATOR_SECRET")
    # create instance of "authenticator app"
    totp = pyotp.TOTP(authenticator_secret)
    enrollment_index = login_gov.enter_otp(totp.now())

    enrollment_index.enroll("Test User", "4111 1111 1111 1111", "12/34", "123")

    # enrollment can take a bit
    page.wait_for_timeout(10000)

    success_message = page.get_by_text("You can now use your contactless card to tap to ride with a reduced fare!")
    expect(success_message).to_be_visible()


def test_calfresh_cardholder_flow(context: BrowserContext, base_url):
    page = context.new_page()

    page.goto(base_url)

    index = Index(page)
    eligibility_index = index.select_agency("California State Transit")
    eligibility_start = eligibility_index.select_flow("CalFresh Cardholder")

    login_gov = eligibility_start.get_started_with_login_gov()

    username = os.environ.get("PLAYWRIGHT_LOGIN_GOV_CALFRESH_USERNAME")
    password = os.environ.get("PLAYWRIGHT_LOGIN_GOV_CALFRESH_PASSWORD")
    login_gov.sign_in(username, password)

    authenticator_secret = os.environ.get("PLAYWRIGHT_LOGIN_GOV_CALFRESH_AUTHENTICATOR_SECRET")
    # create instance of "authenticator app"
    totp = pyotp.TOTP(authenticator_secret)
    enrollment_index = login_gov.enter_otp(totp.now())

    enrollment_index.enroll("Test User", "4111 1111 1111 1111", "12/34", "123")

    # enrollment can take a bit
    page.wait_for_timeout(10000)

    reenrollment_error_message = page.get_by_text("You are still enrolled in this benefit")
    expect(reenrollment_error_message).to_be_visible()
