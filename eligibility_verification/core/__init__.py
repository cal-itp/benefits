"""
The core application: Houses base templates and reusable models and components.
"""
from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    name = "eligibility_verification.core"
    label = "core"
    verbose_name = "Core"


default_app_config = "eligibility_verification.core.CoreAppConfig"
