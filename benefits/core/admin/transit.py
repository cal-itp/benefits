from django.conf import settings
from django.contrib import admin

from benefits.core import models
from .users import is_staff_member_or_superuser


@admin.register(models.TransitAgency)
class TransitAgencyAdmin(admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "eligibility_api_private_key",
                    "eligibility_api_public_key",
                    "sso_domain",
                    "littlepay_config",
                    "switchio_config",
                ]
            )

        return fields or super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "eligibility_api_id",
                    "transit_processor",
                ]
            )

        return fields or super().get_readonly_fields(request, obj)

    def has_add_permission(self, request):
        if settings.RUNTIME_ENVIRONMENT() != settings.RUNTIME_ENVS.PROD:
            return True
        elif request.user and is_staff_member_or_superuser(request.user):
            return True
        else:
            return False


@admin.register(models.TransitProcessor)
class TransitProcessorAdmin(admin.ModelAdmin):

    def get_exclude(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend([])

        return fields or super().get_exclude(request, obj)

    def has_add_permission(self, request):
        if settings.RUNTIME_ENVIRONMENT() != settings.RUNTIME_ENVS.PROD:
            return True
        elif request.user and request.user.is_superuser:
            return True
        else:
            return False
