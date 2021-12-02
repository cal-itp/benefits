"""
The core application: django-modeltranslations registration
https://django-modeltranslation.readthedocs.io/en/latest/registration.html
"""
from modeltranslation.translator import register, TranslationOptions

from . import models


@register(models.I18nText)
class I18nTextTranslationOptions(TranslationOptions):
    fields = ["text"]
