from django.contrib import admin

from benefits.core import models


@admin.register(models.PemData)
class PemDataAdmin(admin.ModelAdmin):
    list_display = ("label",)
