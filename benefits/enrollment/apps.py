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
