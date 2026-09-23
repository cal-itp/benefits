"""
The enrollment application: Allows user to enroll payment device for benefits.
"""

import logging

from django.apps import AppConfig

from benefits.enrollment.registry import TransitProcessorRegistry

logger = logging.getLogger(__name__)


class EnrollmentAppConfig(AppConfig):
    name = "benefits.enrollment"
    label = "enrollment"
    verbose_name = "Benefits Enrollment"

    def ready(self):
        logger.debug(f"Currently registered transit processors: {TransitProcessorRegistry.entries}")


class TransitProcessorAppConfigMixin:
    def ready(self):
        TransitProcessorRegistry.add(self.system_name)
        super().ready()

    @property
    def group_model(self):
        group_model_name = self.system_name.capitalize() + "Group"
        return getattr(self.models_module, group_model_name)

    @property
    def system_name_for_display(self):
        return self.system_name.capitalize()
