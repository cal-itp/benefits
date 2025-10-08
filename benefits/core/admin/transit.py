from django.contrib import admin

from benefits.core import models
from .mixins import StaffPermissionMixin, SuperuserPermissionMixin


@admin.register(models.EligibilityApiConfig)
class EligibilityApiConfigAdmin(SuperuserPermissionMixin, admin.ModelAdmin):
    pass


@admin.register(models.TransitAgency)
class TransitAgencyAdmin(StaffPermissionMixin, admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "sso_domain",
                ]
            )

        return fields or super().get_exclude(request, obj)
