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
    transit_processors = TransitProcessorRegistry()

    def ready(self):
        logger.debug(f"Currently registered transit processors: {list(self.transit_processors.entries.keys())}")


class TransitProcessorAppConfigMixin:
    def ready(self):
        from django.apps import apps

        enrollment_app_config = apps.get_app_config(EnrollmentAppConfig.label)
        transit_processors = enrollment_app_config.transit_processors
        transit_processors.add(self.system_name, self.module)
        super().ready()

    @property
    def system_name_for_display(self):
        return self.system_name.capitalize()
