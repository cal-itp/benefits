"""
The core application: Admin interface configuration.
"""
from benefits.settings import ADMIN


if ADMIN:
    import logging
    from django.contrib import admin
    from modeltranslation.admin import TranslationAdmin
    from . import models

    logger = logging.getLogger(__name__)

    for model in [
        models.EligibilityType,
        models.EligibilityVerifier,
        models.Icon,
        models.Image,
        models.MediaItem,
        models.Page,
        models.PageNavigation,
        models.PaymentProcessor,
        models.PemData,
        models.TransitAgency,
    ]:
        logger.debug(f"Register {model.__name__}")
        admin.site.register(model)

    class I18nTextAdmin(TranslationAdmin):
        pass

    logger.debug(f"Register {models.I18nText.__name__} with admin class {I18nTextAdmin.__name__}")
    admin.site.register(models.I18nText, I18nTextAdmin)
