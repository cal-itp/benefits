from django.contrib import admin

from benefits.enrollment_switchio import models


admin.site.register(models.SwitchioGroup)


@admin.register(models.SwitchioConfig)
class SwitchioConfigAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        """
        This controls whether the model shows up in the main list of models.
        """
        # we don't want to display SwitchioConfig on the main list.
        # the user should view it from the TransitAgency.
        return False
