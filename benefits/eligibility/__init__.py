"""
The eligibility application: Verifies eligibility for discounts.
"""
from django.apps import AppConfig


class EligibilityAppConfig(AppConfig):
    name = "benefits.eligibility"
    label = "eligibility"
    verbose_name = "Eligibility Verification"


default_app_config = "benefits.eligibility.EligibilityAppConfig"
