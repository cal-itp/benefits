from django.contrib import admin

from benefits.enrollment_littlepay import models

admin.site.register(models.LittlepayConfig)
admin.site.register(models.LittlepayGroup)
