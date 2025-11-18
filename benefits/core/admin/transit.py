from django.conf import settings
from django.contrib import admin

from benefits.core import models

from .users import is_staff_member_or_superuser


@admin.register(models.EligibilityApiConfig)
class EligibilityApiConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if request.user and request.user.is_superuser:
            return True
        else:
            return False

    def has_view_permission(self, request, *args, **kwargs):
        if request.user and request.user.is_superuser:
            return True
        else:
            return False


@admin.register(models.TransitAgency)
class TransitAgencyAdmin(admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "sso_domain",
                ]
            )

        return fields or super().get_exclude(request, obj)

    def has_add_permission(self, request):
        if settings.RUNTIME_ENVIRONMENT() != settings.RUNTIME_ENVS.PROD:
            return True
        elif request.user and is_staff_member_or_superuser(request.user):
            return True
        else:
            return False
