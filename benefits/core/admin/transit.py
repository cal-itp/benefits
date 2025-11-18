from django.contrib import admin

from benefits.core import models
from .mixins import StaffPermissionMixin


@admin.register(models.TransitAgency)
class TransitAgencyAdmin(StaffPermissionMixin, admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "eligibility_api_private_key",
                    "eligibility_api_public_key",
                    "sso_domain",
                ]
            )

        return fields or super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "eligibility_api_id",
                ]
            )

        return fields or super().get_readonly_fields(request, obj)
