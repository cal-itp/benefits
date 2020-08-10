"""
The core application: Admin interface configuration.
"""
from benefits.settings import ADMIN


if ADMIN:
    from django.contrib import admin
    from . import models

    admin.site.register(models.EligibilityType)
    admin.site.register(models.EligibilityVerifier)
    admin.site.register(models.TransitAgency)
    admin.site.register(models.DiscountProvider)
