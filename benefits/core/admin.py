"""
The core application: Admin interface configuration.
"""
from benefits.settings import ADMIN


if ADMIN:
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
        models.EligibilityLink,
    ]:
        logger.debug(f"Register {model.__name__}")
        admin.site.register(model)
