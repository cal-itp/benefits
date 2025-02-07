from django.conf import settings
from django.contrib import admin

from benefits.core import models


@admin.register(models.ClaimsProvider)
class ClaimsProviderAdmin(admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(["client_id_secret_name"])

        return fields or super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "sign_out_button_template",
                    "sign_out_link_template",
                    "authority",
                    "scheme",
                ]
            )

        return fields or super().get_readonly_fields(request, obj)

    def has_add_permission(self, request):
        if settings.RUNTIME_ENVIRONMENT() != settings.RUNTIME_ENVS.PROD:
            return True
        elif request.user and request.user.is_superuser:
            return True
        else:
            return False
