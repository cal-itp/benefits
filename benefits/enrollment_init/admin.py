from django.contrib import admin

from benefits.core.admin.mixins import StaffPermissionMixin
from benefits.enrollment_init import models


@admin.register(models.InitConfig)
class InitConfigAdmin(StaffPermissionMixin, admin.ModelAdmin):
    pass


@admin.register(models.InitGroup)
class InitGroupAdmin(StaffPermissionMixin, admin.ModelAdmin):
    pass
