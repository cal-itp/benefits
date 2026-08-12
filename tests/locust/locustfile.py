import os
import random
from urllib.parse import urljoin

import pyotp
from bs4 import BeautifulSoup
from locust import HttpUser, constant_pacing, events, task

USER_EMAIL = os.environ["LOCUST_LOGIN_GOV_OLDER_ADULT_USER_EMAIL"]
USER_PASSWORD = os.environ["LOCUST_LOGIN_GOV_OLDER_ADULT_USER_PASSWORD"]
TOTP_SECRET = os.environ["LOCUST_LOGIN_GOV_OLDER_ADULT_AUTHENTICATOR_SECRET"]
CARD_TOKEN = os.environ["LOCUST_CARD_TOKEN"]

# Experiment design
# -----------------
#
# User distribution
# https://docs.locust.io/en/stable/writing-a-locustfile.html#weight-and-fixed-count-attributes
# Use weight to create eligible vs ineligible users
# EligibleUser gets 93% of the total users (93/100, weight=93)
# IneligibleUser gets 7% of the total users (7/100, weight=7)
# Based on Amplitude data (last 90 days)
#
# Load distribution
# https://docs.locust.io/en/stable/writing-a-locustfile.html#wait-time-attribute
# Pick a target_rate (users/min)
# Pick number_of_concurrent_users (users)
# Calculate the pacing_time (seconds)
# pacing_time = 60 * number_of_concurrent_users / target_rate


def csrf_token(response, element=None, name_attribute_value=None, csrf_value_attribute_name=None) -> str:
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find(element, {"name": name_attribute_value})[csrf_value_attribute_name]


def page_title(response) -> str:
    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("title")
    return title_tag.text.strip() if title_tag else "No Title Found"


class EligibleUser(HttpUser):
    weight = 93

    @task
    def complete_entire_flow(self):
        try:
            agencies = ["mst", "sbmtd", "sacrt"]
            start_agency = random.choice(agencies)

            # /
            with self.client.get("/", catch_response=True) as index:
                print(f"index: {page_title(index)}")

            # Select agency
            with self.client.post(
                "/",
                data={
                    "csrfmiddlewaretoken": csrf_token(
                        index, element="input", name_attribute_value="csrfmiddlewaretoken", csrf_value_attribute_name="value"
                    ),
                    "select_transit_agency": start_agency,
                },
                catch_response=True,
            ) as eligibility:
                if eligibility.status_code != 200:
                    eligibility.failure(f"Failed to select agency. Status code: {eligibility.status_code}")
                    return
                print(f"eligibility: {page_title(eligibility)}")

            # Select enrollment flow
            with self.client.post(
                "/eligibility/",
                data={
                    "csrfmiddlewaretoken": csrf_token(
                        eligibility,
                        element="input",
                        name_attribute_value="csrfmiddlewaretoken",
                        csrf_value_attribute_name="value",
                    ),
                    "flow": "1",
                },
                catch_response=True,
            ) as start:
                print(f"start: {page_title(start)}")

            # Get started with Login.gov
            with self.client.get("/oauth/login", allow_redirects=True, catch_response=True) as login_response:
                print(f"login: {page_title(login_response)}")
            soup = BeautifulSoup(login_response.text, "html.parser")
            form = soup.find("form")
            if not form or not form.get("action"):
                print("Could not find login form action")
                return
            login_post_url = urljoin(login_response.url, form["action"])
            print(f"posturl: {login_post_url}")

            # Login.gov sign in
            login_gov = self.client.post(
                login_post_url,
                data={
                    "authenticity_token": csrf_token(
                        login_response, element="meta", name_attribute_value="csrf-token", csrf_value_attribute_name="content"
                    ),
                    "user[email]": USER_EMAIL,
                    "user[password]": USER_PASSWORD,
                },
            )
            print(f"login: {page_title(login_gov)}")

            # Multi-factor authentication
            current_totp_code = pyotp.TOTP(TOTP_SECRET).now()
            mfa_response = self.client.post(
                login_gov.url,
                data={
                    "authenticity_token": csrf_token(
                        login_gov, element="meta", name_attribute_value="csrf-token", csrf_value_attribute_name="content"
                    ),
                    "code": current_totp_code,
                },
                allow_redirects=True,
            )
            print(f"mfa: {page_title(mfa_response)}")

            # login.gov <> IdG <> Benefits
            # LLM assisted code
            # Handle any JavaScript "auto-submit" forms which implement the redirect behavior
            # This is required since locust does not run JavaScript or drive a real browser
            current_response = mfa_response
            while True:
                soup = BeautifulSoup(current_response.text, "html.parser")
                title_tag = soup.find("title")
                title_text = title_tag.text if title_tag else ""

                form = soup.find("form")

                # 1. Is there an auto-submit form? (Used by Login.gov and IdG)
                if form and (
                    "Redirect" in title_text
                    or "Submit" in title_text
                    or "Working" in title_text
                    or "/external/callback" in current_response.url
                ):
                    action_url = form.get("action")
                    action_url = urljoin(current_response.url, action_url) if action_url else current_response.url

                    # Extract all hidden security tokens (code, state, etc.)
                    payload = {
                        inp.get("name"): inp.get("value") for inp in form.find_all("input", type="hidden") if inp.get("name")
                    }
                    print(f"Auto-submitting form to: {action_url}")

                    current_response = self.client.post(action_url, data=payload, allow_redirects=True)
                    print(f"Landed on: {current_response.status_code} | {current_response.url}")

                # 2. Is there a fallback 'Click Here' link?
                elif "Redirect" in title_text and soup.find("a"):
                    action_url = urljoin(current_response.url, soup.find("a").get("href"))

                    print(f"Following fallback link to: {action_url}")
                    current_response = self.client.get(action_url, allow_redirects=True)
                    print(f"Landed on: {current_response.status_code} | {current_response.url}")

                else:
                    # We have reached a normal page (or are completely stuck)
                    if "Redirect" in title_text:
                        # If we are stuck on a redirect page, print the HTML so you can see exactly why
                        print("Stuck! Found 'Redirecting' page but no form, meta, or link. HTML Dump:")
                        print(current_response.text)
                    break
            print(f"eligible: {page_title(current_response)}")

            # Littlepay enrollment
            # Simulate the background initialization request the browser makes
            self.client.get("/littlepay/token", catch_response=True)
            # Extract the success form
            soup_enroll = BeautifulSoup(current_response.text, "html.parser")
            success_form = soup_enroll.find("form", id="form-card-tokenize-success")
            if not success_form:
                print("Could not find the success form")
                return
            action_url = success_form.get("action")
            action_url = urljoin(current_response.url, action_url)
            # POST the hidden form to complete the enrollment
            enrollment_response = self.client.post(
                action_url,
                data={
                    "csrfmiddlewaretoken": csrf_token(
                        current_response,
                        element="input",
                        name_attribute_value="csrfmiddlewaretoken",
                        csrf_value_attribute_name="value",
                    ),
                    "card_token": CARD_TOKEN,
                },
                allow_redirects=True,
            )

            # Success
            print(f"Enrollment submission returned: {enrollment_response.status_code}")
            print(f"Final Success Title: {page_title(enrollment_response)}")
        finally:
            # Log out of Login.gov (via Benefits)
            # to avoid having to conditionally skip the MFA page the next time the user runs and is still logged in
            self.client.get("/oauth/logout", catch_response=True)
            # Reset cookies on client for the next time this user spawns
            self.client.cookies.clear()


class IneligibleUser(HttpUser):
    weight = 7

    @task
    def complete_entire_flow(self):
        start_agency = "vctc"

        # STEP 1: Start the journey
        response = self.client.get(f"/{start_agency}")

        # (Sequential form steps will go here)
        print(response)


@events.init_command_line_parser.add_listener
def _(parser):
    # https://docs.locust.io/en/stable/extending-locust.html#custom-arguments
    # Add a custom argument for the target rate
    parser.add_argument("--target-rate", type=float, default=1, help="Target users per minute for dynamic pacing")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # https://docs.locust.io/en/stable/writing-a-locustfile.html#init
    num_users = environment.parsed_options.num_users
    target_rate = environment.parsed_options.target_rate
    calculated_spawn_rate = target_rate / 60
    environment.parsed_options.spawn_rate = calculated_spawn_rate

    # Calculate the "pacing time" needed to have r users per minute (target rate) running
    pacing_seconds = 60 * num_users / target_rate

    # Print to the console when the test starts
    print("---")
    print(f"Targeting {target_rate} users/min with {num_users} users.")
    print(f"Dynamic Pacing set to {pacing_seconds:.1f} seconds.")
    print("---")

    # Inject the calculated wait time into the User classes
    EligibleUser.wait_time = constant_pacing(pacing_seconds)
    IneligibleUser.wait_time = constant_pacing(pacing_seconds)
