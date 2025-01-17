from django.contrib import admin

from benefits.core import models


@admin.register(models.TransitAgency)
class TransitAgencyAdmin(admin.ModelAdmin):  # pragma: no cover
    def get_exclude(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "eligibility_api_private_key",
                "eligibility_api_public_key",
                "transit_processor_client_id",
                "transit_processor_client_secret_name",
                "transit_processor_audience",
            ]
        else:
            return super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "eligibility_api_id",
                "transit_processor",
                "index_template_override",
                "eligibility_index_template_override",
            ]
        else:
            return super().get_readonly_fields(request, obj)


@admin.register(models.TransitProcessor)
class TransitProcessorAdmin(admin.ModelAdmin):  # pragma: no cover
    def get_exclude(self, request, obj=None):
        if not request.user.is_superuser:
            return []
        else:
            return super().get_exclude(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "card_tokenize_url",
                "card_tokenize_func",
                "card_tokenize_env",
            ]
        else:
            return super().get_readonly_fields(request, obj)
