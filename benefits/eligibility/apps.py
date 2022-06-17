"""
The eligibility application: Verifies eligibility for benefits.
"""
from django.apps import AppConfig


class EligibilityAppConfig(AppConfig):
    name = "benefits.eligibility"
    label = "eligibility"
    verbose_name = "Eligibility Verification"
