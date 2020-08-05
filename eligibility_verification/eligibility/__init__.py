from django.apps import AppConfig


class EligibilityAppConfig(AppConfig):
    name = 'eligibility_verification.eligibility'
    label = 'eligibility'
    verbose_name = 'Eligibility Verification'


default_app_config = 'eligibility_verification.eligibility.EligibilityAppConfig'
