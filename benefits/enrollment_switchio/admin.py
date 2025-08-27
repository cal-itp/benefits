from django.contrib import admin

from benefits.enrollment_switchio import models


admin.site.register(models.SwitchioConfig)
admin.site.register(models.SwitchioGroup)
