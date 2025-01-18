from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest

from adminsortable2.admin import SortableAdminMixin

from benefits.core import models
from .users import is_staff_or_superuser


@admin.register(models.EnrollmentEvent)
class EnrollmentEventAdmin(admin.ModelAdmin):
    list_display = ("enrollment_datetime", "transit_agency", "enrollment_flow", "enrollment_method", "verified_by")

    def has_add_permission(self, request: HttpRequest, obj=None):
        if settings.RUNTIME_ENVIRONMENT() == settings.RUNTIME_ENVS.PROD:
            return False
        elif request.user and is_staff_or_superuser(request.user):
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
        elif request.user and is_staff_or_superuser(request.user):
            return True
        else:
            return False

    def has_view_permission(self, request: HttpRequest, obj=None):
        if request.user and is_staff_or_superuser(request.user):
            return True
        else:
            return False


@admin.register(models.EnrollmentFlow)
class SortableEnrollmentFlowAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("label", "transit_agency", "supported_enrollment_methods")

    def get_exclude(self, request, obj=None):
        fields = []

        if not is_staff_or_superuser(request.user):
            fields.extend(
                [
                    "claims_scope",
                    "claims_eligibility_claim",
                    "claims_scheme_override",
                    "eligibility_api_url",
                    "eligibility_form_class",
                ]
            )
        if not request.user.is_superuser:
            fields.extend(
                [
                    "eligibility_api_auth_header",
                    "eligibility_api_auth_key_secret_name",
                    "eligibility_api_public_key",
                    "eligibility_api_jwe_cek_enc",
                    "eligibility_api_jwe_encryption_alg",
                    "eligibility_api_jws_signing_alg",
                ]
            )

        return fields or super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if not is_staff_or_superuser(request.user):
            fields.extend(
                [
                    "system_name",
                    "transit_agency",
                    "supported_enrollment_methods",
                    "claims_provider",
                    "supports_expiration",
                ]
            )
        if not request.user.is_superuser:
            fields.extend(
                [
                    "eligibility_api_url",
                    "eligibility_form_class",
                    "selection_label_template_override",
                    "eligibility_start_template_override",
                    "eligibility_unverified_template_override",
                    "help_template",
                    "enrollment_index_template_override",
                    "reenrollment_error_template",
                    "enrollment_success_template_override",
                ]
            )

        return fields or super().get_readonly_fields(request, obj)

    def has_add_permission(self, request: HttpRequest, obj=None):
        if settings.RUNTIME_ENVIRONMENT() != settings.RUNTIME_ENVS.PROD:
            return True
        elif request.user and is_staff_or_superuser(request.user):
            return True
        else:
            return False
