from django.contrib import admin

from benefits.enrollment_littlepay import models

admin.site.register(models.LittlepayGroup)


@admin.register(models.OldLittlepayConfig)
class LittlepayConfigAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        """
        This controls whether the model shows up in the main list of models.
        """
        # we don't want to display LittlepayConfig on the main list.
        # the user should view it from the TransitAgency.
        return False
