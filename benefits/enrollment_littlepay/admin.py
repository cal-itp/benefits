from django.contrib import admin

from benefits.core.admin.mixins import StaffPermissionMixin
from benefits.enrollment_littlepay import models


@admin.register(models.LittlepayConfig)
class LittlepayConfigAdmin(StaffPermissionMixin, admin.ModelAdmin):
    pass


@admin.register(models.LittlepayGroup)
class LittlepayGroupAdmin(StaffPermissionMixin, admin.ModelAdmin):
    pass
