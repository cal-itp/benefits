from django.apps import AppConfig

from benefits.enrollment.apps import TransitProcessorAppConfigMixin


class EnrollmentSwitchioConfig(TransitProcessorAppConfigMixin, AppConfig):
    name = "benefits.enrollment_switchio"
    label = "enrollment_switchio"
    system_name = "switchio"
