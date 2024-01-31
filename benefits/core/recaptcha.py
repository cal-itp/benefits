"""
The core application: helpers to work with reCAPTCHA.
"""

import requests

from django.conf import settings


DATA_FIELD = "g-recaptcha-response"


def has_error(form) -> bool:
    """True if the given form has a reCAPTCHA error. False otherwise."""
    return any([s for (_, v) in form.errors.items() for s in v if "reCAPTCHA" in s])


def verify(form_data: dict) -> bool:
    """
    Check with Google reCAPTCHA if the given response is a valid user.
    See https://developers.google.com/recaptcha/docs/verify
    """
    if not settings.RECAPTCHA_ENABLED:
        return True

    if not form_data or DATA_FIELD not in form_data:
        return False

    payload = dict(secret=settings.RECAPTCHA_SECRET_KEY, response=form_data[DATA_FIELD])
    response = requests.post(settings.RECAPTCHA_VERIFY_URL, payload, timeout=settings.REQUESTS_TIMEOUT).json()

    return bool(response["success"])
