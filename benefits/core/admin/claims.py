from django.contrib import admin

from benefits.core import models


@admin.register(models.ClaimsProvider)
class ClaimsProviderAdmin(admin.ModelAdmin):  # pragma: no cover
    def get_exclude(self, request, obj=None):
        if not request.user.is_superuser:
            return ["client_id_secret_name"]
        else:
            return super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "sign_out_button_template",
                "sign_out_link_template",
                "authority",
                "scheme",
            ]
        else:
            return super().get_readonly_fields(request, obj)
