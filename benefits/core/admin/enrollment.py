from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest

from adminsortable2.admin import SortableAdminMixin

from benefits.core import models
from .users import is_staff_or_superuser


@admin.register(models.EnrollmentEvent)
class EnrollmentEventAdmin(admin.ModelAdmin):  # pragma: no cover
    list_display = ("enrollment_datetime", "transit_agency", "enrollment_flow", "enrollment_method", "verified_by")

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        return ["id"]

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
class SortableEnrollmentFlowAdmin(SortableAdminMixin, admin.ModelAdmin):  # pragma: no cover
    list_display = ("label", "transit_agency", "supported_enrollment_methods")

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
                "eligibility_start_template_override",
                "eligibility_unverified_template_override",
                "help_template",
                "selection_label_template_override",
                "claims_scheme_override",
                "enrollment_index_template",
                "reenrollment_error_template",
                "enrollment_success_template_override",
            ]
        else:
            return super().get_readonly_fields(request, obj)
