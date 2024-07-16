"""
The core application: Admin interface configuration.
"""

import logging
import requests

from adminsortable2.admin import SortableAdminMixin
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from . import models

logger = logging.getLogger(__name__)


GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
STAFF_GROUP_NAME = "Cal-ITP"

logger.debug("Register models with admin site")
admin.site.register(models.PemData)


@admin.register(models.AuthProvider)
class AuthProviderAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EligibilityType)
class EligibilityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EligibilityVerifier)
class SortableEligibilityVerifierAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.PaymentProcessor)
class PaymentProcessorAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TransitAgency)
class TransitAgencyAdmin(admin.ModelAdmin):
    pass


def pre_login_user(user, request):
    logger.debug(f"Running pre-login callback for user: {user.username}")
    add_google_sso_userinfo(user, request)
    add_staff_user_to_group(user, request)


def add_google_sso_userinfo(user, request):
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


def add_staff_user_to_group(user, request):
    if user.email in settings.GOOGLE_SSO_STAFF_LIST:
        staff_group = Group.objects.get(name=STAFF_GROUP_NAME)
        user.groups.add(staff_group)
