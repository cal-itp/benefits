from django.contrib import admin
from django.contrib.auth.models import Group

from benefits.core import models
from .mixins import StaffPermissionMixin, SuperuserPermissionMixin


@admin.register(models.EligibilityApiConfig)
class EligibilityApiConfigAdmin(SuperuserPermissionMixin, admin.ModelAdmin):
    pass


@admin.register(models.TransitAgency)
class TransitAgencyAdmin(StaffPermissionMixin, admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        fields = []

        if not request.user.is_superuser:
            fields.extend(
                [
                    "sso_domain",
                ]
            )

        return fields or super().get_exclude(request, obj)

    def save_model(self, request, obj, form, change):

        if not change:
            staff_group_name = f"{obj.short_name} Staff"
            staff_group = Group.objects.create(name=staff_group_name)
            obj.staff_group = staff_group
        if not change:
            cs_group_name = f"{obj.short_name} Customer Service"
            customer_service_group = Group.objects.create(name=cs_group_name)
            obj.customer_service_group = customer_service_group

        super().save_model(request, obj, form, change)
