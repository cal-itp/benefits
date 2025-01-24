from django.contrib import admin

from benefits.core import models
from .users import is_staff_or_superuser


@admin.register(models.ClaimsProvider)
class ClaimsProviderAdmin(admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        fields = []

        if not is_staff_or_superuser(request.user):
            fields.extend(["authority", "scheme"])
        if not request.user.is_superuser:
            fields.extend(["client_id_secret_name"])

        return fields or super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if not is_staff_or_superuser(request.user):
            fields.extend(["client_name"])
        if not request.user.is_superuser:
            fields.extend(
                [
                    "sign_out_button_template",
                    "sign_out_link_template",
                    "client_id_secret_name",
                    "authority",
                    "scheme",
                ]
            )

        return fields or super().get_readonly_fields(request, obj)
