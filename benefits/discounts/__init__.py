"""
The discounts application: Allows user to associate payment device with discounts.
"""
from django.apps import AppConfig


class DiscountsAppConfig(AppConfig):
    name = "benefits.discounts"
    label = "discounts"
    verbose_name = "Eligibility Verification: Discounts"


default_app_config = "benefits.discounts.DiscountsAppConfig"
