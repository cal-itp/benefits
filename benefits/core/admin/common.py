from django.contrib import admin
from django.http import HttpRequest

from benefits.core import models


@admin.register(models.PemData)
class PemDataAdmin(admin.ModelAdmin):

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
