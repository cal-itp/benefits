"""
The core application: Admin interface configuration.
"""

import logging
import requests

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from . import models

logger = logging.getLogger(__name__)


GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


for model in [
    models.EligibilityVerifier,
    models.PaymentProcessor,
    models.PemData,
    models.TransitAgency,
]:
    logger.debug(f"Register {model.__name__}")
    admin.site.register(model)


class EligibilityTypeForm(forms.ModelForm):
    class Meta:
        model = models.EligibilityType
        exclude = []

    def clean(self):
        cleaned_data = super().clean()
        supports_expiration = cleaned_data.get("supports_expiration")
        expiration_days = cleaned_data.get("expiration_days")
        expiration_reenrollment_days = cleaned_data.get("expiration_reenrollment_days")

        if supports_expiration:
            message = "When support_expiration is True, this value must be greater than 0."
            if expiration_days is None or expiration_days <= 0:
                self.add_error("expiration_days", ValidationError(message))
            if expiration_reenrollment_days is None or expiration_reenrollment_days <= 0:
                self.add_error("expiration_reenrollment_days", ValidationError(message))


class EligibilityTypeAdmin(admin.ModelAdmin):
    form = EligibilityTypeForm


logger.debug(f"Register {models.EligibilityType.__name__} with custom admin {EligibilityTypeAdmin.__name__}")
admin.site.register(models.EligibilityType, EligibilityTypeAdmin)


def pre_login_user(user, request):
    logger.debug(f"Running pre-login callback for user: {user.username}")
    token = request.session.get("google_sso_access_token")
    if token:
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Request Google user info to get name and email
        response = requests.get(GOOGLE_USER_INFO_URL, headers=headers, timeout=settings.REQUESTS_TIMEOUT)
        user_data = response.json()
        logger.debug(f"Updating user data from Google for user with email: {user_data['email']}")

        user.first_name = user_data["given_name"]
        user.last_name = user_data["family_name"]
        user.username = user_data["email"]
        user.email = user_data["email"]
        user.save()
    else:
        logger.warning("google_sso_access_token not found in session.")
