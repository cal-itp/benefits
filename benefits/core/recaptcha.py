"""
The core application: helpers to work with reCAPTCHA.
"""
import requests

from benefits.settings import RECAPTCHA_ENABLED, RECAPTCHA_SECRET_KEY, RECAPTCHA_VERIFY_URL


_POST_DATA = "g-recaptcha-response"


def verify(form_data: dict) -> bool:
    """
    Check with Google reCAPTCHA if the given response is a valid user.
    See https://developers.google.com/recaptcha/docs/verify
    """
    if not RECAPTCHA_ENABLED:
        return True

    if not form_data or _POST_DATA not in form_data:
        return False

    payload = dict(secret=RECAPTCHA_SECRET_KEY, response=form_data[_POST_DATA])
    response = requests.post(RECAPTCHA_VERIFY_URL, payload).json()

    return bool(response["success"])
