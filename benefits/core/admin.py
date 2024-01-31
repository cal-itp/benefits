"""
The core application: Admin interface configuration.
"""

from django.conf import settings


if settings.ADMIN:
    import logging
    from django.contrib import admin
    from . import models

    logger = logging.getLogger(__name__)

    for model in [
        models.EligibilityType,
        models.EligibilityVerifier,
        models.PaymentProcessor,
        models.PemData,
        models.TransitAgency,
    ]:
        logger.debug(f"Register {model.__name__}")
        admin.site.register(model)
