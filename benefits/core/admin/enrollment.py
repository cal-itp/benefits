from adminsortable2.admin import SortableAdminMixin
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from benefits.core import models

from .mixins import ProdReadOnlyPermissionMixin, StaffPermissionMixin, SuperuserPermissionMixin


@admin.register(models.EnrollmentEvent)
class EnrollmentEventAdmin(ProdReadOnlyPermissionMixin, admin.ModelAdmin):
    list_display = ("enrollment_datetime", "transit_agency", "enrollment_flow", "enrollment_method", "verified_by")
    ordering = ("-enrollment_datetime",)


@admin.register(models.EligibilityApiVerificationRequest)
class EligibilityApiVerificationRequestAdmin(SuperuserPermissionMixin, admin.ModelAdmin):
    list_display = ("label", "api_url")


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
class SortableEnrollmentFlowAdmin(StaffPermissionMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ("label", "transit_agency", "supported_enrollment_methods")
    form = EnrollmentFlowForm
