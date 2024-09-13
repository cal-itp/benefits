"""
The core application: Admin interface configuration.
"""

import logging
import requests

from adminsortable2.admin import SortableAdminMixin
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpRequest

from . import models

logger = logging.getLogger(__name__)


GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

logger.debug("Register models with admin site")
admin.site.register(models.PemData)


@admin.register(models.ClaimsProvider)
class ClaimsProviderAdmin(admin.ModelAdmin):  # pragma: no cover
    def get_exclude(self, request, obj=None):
        if not request.user.is_superuser:
            return ["client_id_secret_name"]
        else:
            return super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "sign_out_button_template",
                "sign_out_link_template",
                "authority",
                "scheme",
            ]
        else:
            return super().get_readonly_fields(request, obj)


@admin.register(models.EnrollmentFlow)
class SortableEnrollmentFlowAdmin(SortableAdminMixin, admin.ModelAdmin):  # pragma: no cover
    def get_exclude(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "eligibility_api_auth_header",
                "eligibility_api_auth_key_secret_name",
                "eligibility_api_public_key",
                "eligibility_api_jwe_cek_enc",
                "eligibility_api_jwe_encryption_alg",
                "eligibility_api_jws_signing_alg",
                "eligibility_form_class",
            ]
        else:
            return super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "claims_provider",
                "eligibility_api_url",
                "eligibility_start_template",
                "eligibility_unverified_template",
                "help_template",
                "selection_label_template",
                "claims_scheme_override",
                "enrollment_index_template",
                "reenrollment_error_template",
                "enrollment_success_template",
            ]
        else:
            return super().get_readonly_fields(request, obj)


@admin.register(models.TransitProcessor)
class TransitProcessorAdmin(admin.ModelAdmin):  # pragma: no cover
    def get_exclude(self, request, obj=None):
        if not request.user.is_superuser:
            return []
        else:
            return super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "card_tokenize_url",
                "card_tokenize_func",
                "card_tokenize_env",
            ]
        else:
            return super().get_readonly_fields(request, obj)


@admin.register(models.TransitAgency)
class TransitAgencyAdmin(admin.ModelAdmin):  # pragma: no cover
    def get_exclude(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "eligibility_api_private_key",
                "eligibility_api_public_key",
                "eligibility_api_jws_signing_alg",
                "transit_processor_client_id",
                "transit_processor_client_secret_name",
                "transit_processor_audience",
            ]
        else:
            return super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "eligibility_api_id",
                "transit_processor",
                "index_template",
                "eligibility_index_template",
            ]
        else:
            return super().get_readonly_fields(request, obj)


@admin.register(models.EnrollmentEvent)
class EnrollmentEventAdmin(admin.ModelAdmin):  # pragma: no cover
    def has_add_permission(self, request: HttpRequest, obj=None):
        if settings.RUNTIME_ENVIRONMENT() == settings.RUNTIME_ENVS.PROD:
            return False
        elif request.user and (request.user.is_superuser or is_staff_member(request.user)):
            return True
        else:
            return False

    def has_change_permission(self, request: HttpRequest, obj=None):
        if settings.RUNTIME_ENVIRONMENT() == settings.RUNTIME_ENVS.PROD:
            return False
        elif request.user and request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request: HttpRequest, obj=None):
        if settings.RUNTIME_ENVIRONMENT() == settings.RUNTIME_ENVS.PROD:
            return False
        elif request.user and (request.user.is_superuser or is_staff_member(request.user)):
            return True
        else:
            return False

    def has_view_permission(self, request: HttpRequest, obj=None):
        if request.user and (request.user.is_superuser or is_staff_member(request.user)):
            return True
        else:
            return False


def pre_login_user(user, request):
    logger.debug(f"Running pre-login callback for user: {user.username}")
    add_google_sso_userinfo(user, request)
    add_staff_user_to_group(user, request)
    add_transit_agency_staff_user_to_group(user, request)


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
        staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
        staff_group.user_set.add(user)


def add_transit_agency_staff_user_to_group(user, request):
    user_sso_domain = user.email.split("@")[1]
    if user_sso_domain:
        agency = models.TransitAgency.objects.filter(sso_domain=user_sso_domain).first()
        if agency is not None and agency.staff_group:
            agency.staff_group.user_set.add(user)


def is_staff_member(user):
    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    return staff_group.user_set.contains(user)
