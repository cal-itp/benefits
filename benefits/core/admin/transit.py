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

        if not obj:
            # hide these fields when creating a new agency
            fields.extend(["customer_service_group"])

        return fields or super().get_exclude(request, obj)

    def save_model(self, request, obj, form, change):

        if not change:
            cs_group_name = f"{obj.short_name} Customer Service"
            customer_service_group = Group.objects.create(name=cs_group_name)
            obj.customer_service_group = customer_service_group
        elif "short_name" in form.changed_data:
            obj.customer_service_group.name = f"{obj.short_name} Customer Service"
            obj.customer_service_group.save()

        super().save_model(request, obj, form, change)
