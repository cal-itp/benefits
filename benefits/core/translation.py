from modeltranslation.translator import TranslationOptions, register

from benefits.core.models.enrollment import EnrollmentFlow


@register(EnrollmentFlow)
class EnrollmentFlowTranslationOptions(TranslationOptions):
    fields = ("label",)
