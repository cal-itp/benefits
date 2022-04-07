"""
The core application: Houses base templates and reusable models and components.
"""
from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    name = "benefits.core"
    label = "core"
    verbose_name = "Core"
