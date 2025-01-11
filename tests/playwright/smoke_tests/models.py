from playwright.sync_api import Page


class Index:
    def __init__(self, page: Page):
        self.page = page

    def select_agency(self, agency_name):
        page = self.page
        page.get_by_role("link", name="Choose your Provider").click()
        page.get_by_role("link", name=agency_name).click()

        return EligibilityIndex(page)


class EligibilityIndex:
    def __init__(self, page: Page):
        self.page = page

    def select_flow(self, flow_name):
        page = self.page
        page.get_by_label(flow_name).check()
        page.wait_for_load_state("networkidle")  # wait for reCAPTCHA to finish loading
        page.get_by_role("button", name="Choose this benefit").click()

        return EligibilityStart(page)


class EligibilityStart:
    def __init__(self, page: Page):
        self.page = page

    def click_continue(self):
        page = self.page
        page.get_by_role("button", name="Continue").click()

        return EligibilityConfirm(page)

    def get_started_with_login_gov(self):
        page = self.page
        page.get_by_role("link", name="Get started with Login.gov").click()

        return LoginGov(page)

    def continue_to_medicare_gov(self):
        page = self.page
        page.get_by_role("button", name="Continue to Medicare.gov").click()

        return MedicareGov(page)


class EligibilityConfirm:
    def __init__(self, page: Page):
        self.page = page

    def submit_form(self, sub, name):
        page = self.page
        page.get_by_placeholder("12345").click()

        page.get_by_placeholder("12345").fill(sub)
        page.keyboard.press("Tab")

        page.get_by_placeholder("Hernandez-Demarcos").fill(name)

        page.get_by_role("button", name="Find my record").click()

        return EnrollmentIndex(page)


class LoginGov:
    def __init__(self, page: Page):
        self.page = page

    def sign_in(self, username, password):
        page = self.page
        page.get_by_label("Email address").click()
        page.get_by_label("Email address").fill(username)
        page.get_by_label("Email address").press("Tab")

        page.get_by_label("Password", exact=True).fill(password)

        page.get_by_role("button", name="Sign in").click()

    def enter_otp(self, one_time_password):
        page = self.page
        page.get_by_label("One-time code").click()
        page.get_by_label("One-time code").fill(one_time_password)

        page.get_by_role("button", name="Submit").click()

        return EnrollmentIndex(page)


class MedicareGov:
    def __init__(self, page: Page):
        self.page = page

    def log_in(self, username, password):
        page = self.page

        page.get_by_label("Username", exact=True).click()
        page.get_by_label("Username", exact=True).fill(username)

        page.get_by_label("Password").fill(password)

        page.get_by_role("button", name="Log in").click()

    def accept_consent_screen(self):
        page = self.page
        page.get_by_role("button", name="Connect").click()

        return EnrollmentIndex(page)


class EnrollmentIndex:
    def __init__(self, page: Page):
        self.page = page

    def enroll(self, cardholder_name, card_number, expiration, security_code):
        page = self.page

        with page.expect_popup() as popup_info:
            page.get_by_role("button", name="Enroll").click()

        popup = popup_info.value
        popup.wait_for_timeout(3000)

        popup.get_by_text("Cardholder name").click()

        popup.get_by_label("Cardholder name").fill(cardholder_name)
        popup.keyboard.press("Tab")

        popup.get_by_label("Card number").fill(card_number)
        popup.keyboard.press("Tab")

        popup.get_by_label("mm/yy").fill(expiration)
        popup.keyboard.press("Tab")

        popup.get_by_text("Security code", exact=True).click()
        popup.get_by_label("Security code").fill(security_code)

        # trigger form validation - not sure why their form behaves this way
        popup.keyboard.press("Shift+Tab")
        popup.keyboard.press("Shift+Tab")
        popup.keyboard.press("Shift+Tab")
        popup.keyboard.press("Tab")

        popup.get_by_role("group", name="Enter your card details").get_by_role("button").click()
