from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.http import HttpRequest

from adminsortable2.admin import SortableAdminMixin

from benefits.core import models
from .users import is_staff_member_or_superuser


@admin.register(models.EnrollmentEvent)
class EnrollmentEventAdmin(admin.ModelAdmin):
    list_display = ("enrollment_datetime", "transit_agency", "enrollment_flow", "enrollment_method", "verified_by")

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        return ["id"]

    def has_add_permission(self, request: HttpRequest, obj=None):
        if settings.RUNTIME_ENVIRONMENT() == settings.RUNTIME_ENVS.PROD:
            return False
        elif request.user and is_staff_member_or_superuser(request.user):
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
        elif request.user and is_staff_member_or_superuser(request.user):
            return True
        else:
            return False

    def has_view_permission(self, request: HttpRequest, obj=None):
        if request.user and is_staff_member_or_superuser(request.user):
            return True
        else:
            return False


class EnrollmentFlowForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        field_errors = {}
        non_field_errors = []

        supports_expiration = cleaned_data.get("supports_expiration")

        if supports_expiration:
            expiration_days = cleaned_data.get("expiration_days")
            expiration_reenrollment_days = cleaned_data.get("expiration_reenrollment_days")
            reenrollment_error_template = cleaned_data.get("reenrollment_error_template")

            message = "When support_expiration is True, this value must be greater than 0."
            if expiration_days is None or expiration_days <= 0:
                field_errors.update(expiration_days=ValidationError(message))
            if expiration_reenrollment_days is None or expiration_reenrollment_days <= 0:
                field_errors.update(expiration_reenrollment_days=ValidationError(message))
            if not reenrollment_error_template:
                field_errors.update(reenrollment_error_template=ValidationError("Required when supports expiration is True."))

        transit_agency = cleaned_data.get("transit_agency")

        if transit_agency:
            if cleaned_data.get("claims_provider"):
                message = "Required for claims verification."
                needed = dict(
                    claims_scope=cleaned_data.get("claims_scope"),
                    claims_eligibility_claim=cleaned_data.get("claims_eligibility_claim"),
                )
                field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})
            elif cleaned_data.get("eligibility_api_url") and cleaned_data.get("eligibility_form_class"):
                message = "Required for Eligibility API verification."
                needed = dict(
                    eligibility_api_auth_header=cleaned_data.get("eligibility_api_auth_header"),
                    eligibility_api_auth_key_secret_name=cleaned_data.get("eligibility_api_auth_key_secret_name"),
                    eligibility_api_jwe_cek_enc=cleaned_data.get("eligibility_api_jwe_cek_enc"),
                    eligibility_api_jwe_encryption_alg=cleaned_data.get("eligibility_api_jwe_encryption_alg"),
                    eligibility_api_jws_signing_alg=cleaned_data.get("eligibility_api_jws_signing_alg"),
                    eligibility_api_public_key=cleaned_data.get("eligibility_api_public_key"),
                )
                field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

        if field_errors:
            raise ValidationError(field_errors)
        if non_field_errors:
            raise ValidationError(non_field_errors)


@admin.register(models.EnrollmentFlow)
class SortableEnrollmentFlowAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("label", "transit_agency", "supported_enrollment_methods")
    form = EnrollmentFlowForm

    def get_exclude(self, request, obj=None):
        fields = []

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
        elif request.user and is_staff_member_or_superuser(request.user):
            return True
        else:
            return False
