from django.contrib import admin

from benefits.core.admin.mixins import StaffPermissionMixin
from benefits.enrollment_switchio import models


@admin.register(models.SwitchioConfig)
class SwitchioConfigAdmin(StaffPermissionMixin, admin.ModelAdmin):
    pass


@admin.register(models.SwitchioGroup)
class SwitchioGroupAdmin(StaffPermissionMixin, admin.ModelAdmin):
    pass
