from django.contrib import admin
from django.http import HttpRequest

from benefits.core import models


@admin.register(models.PemData)
class PemDataAdmin(admin.ModelAdmin):
    list_display = ("label",)

    def get_exclude(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(["remote_url", "text_secret_name"])

        return fields or super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(["label"])

        return fields or super().get_readonly_fields(request, obj)

    def has_add_permission(self, request: HttpRequest, obj=None):
        if request.user and request.user.is_superuser:
            return True
        else:
            return False
