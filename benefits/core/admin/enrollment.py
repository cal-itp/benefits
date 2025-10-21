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
    ordering = ("-enrollment_datetime",)

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


@admin.register(models.EligibilityApiVerificationRequest)
class EligibilityApiVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ("label", "api_url")

    def has_view_permission(self, request: HttpRequest, obj=None):
        if request.user and request.user.is_superuser:
            return True
        else:
            return False

    def has_add_permission(self, request: HttpRequest, obj=None):
        if request.user and request.user.is_superuser:
            return True
        else:
            return False


class EnrollmentFlowForm(forms.ModelForm):
    def has_field(self, field_name):
        return self.fields.get(field_name) is not None

    def get(self, cleaned_data, field_name):
        """
        If the field is present on the form, simply get the value from the cleaned_data.

        If the field is not present on the form, that means the user doesn't have access to the field,
        so get the value from the form's instance of the object.
        """
        return cleaned_data.get(field_name) if self.has_field(field_name) else getattr(self.instance, field_name)

    def clean(self):
        cleaned_data = super().clean()

        field_errors = {}
        non_field_errors = []

        supports_expiration = cleaned_data.get("supports_expiration")

        if supports_expiration:
            expiration_days = cleaned_data.get("expiration_days")
            expiration_reenrollment_days = cleaned_data.get("expiration_reenrollment_days")

            message = "When support_expiration is True, this value must be greater than 0."
            if expiration_days is None or expiration_days <= 0:
                field_errors.update(expiration_days=ValidationError(message))
            if expiration_reenrollment_days is None or expiration_reenrollment_days <= 0:
                field_errors.update(expiration_reenrollment_days=ValidationError(message))

        transit_agency = cleaned_data.get("transit_agency")

        if transit_agency:
            # these fields might not be on the form, so use helper method to correctly get the value
            eligibility_api_request = self.get(cleaned_data, "api_request")
            claims_request = self.get(cleaned_data, "claims_request")

            if not (claims_request or eligibility_api_request):
                message = (
                    "Must configure either claims verification or Eligibility API verification before"
                    + " adding to a transit agency."
                )
                non_field_errors.append(ValidationError(message))

        for field_name, validation_error in field_errors.items():
            self.add_error(field_name, validation_error)
        for validation_error in non_field_errors:
            self.add_error(None, validation_error)


@admin.register(models.EnrollmentFlow)
class SortableEnrollmentFlowAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("label", "transit_agency", "supported_enrollment_methods")
    form = EnrollmentFlowForm

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "selection_label_template_override",
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
