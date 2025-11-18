from django.contrib import admin

from benefits.core import models
from .mixins import SuperuserPermissionMixin


@admin.register(models.PemData)
class PemDataAdmin(SuperuserPermissionMixin, admin.ModelAdmin):
    pass
