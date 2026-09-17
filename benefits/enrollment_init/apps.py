from django.apps import AppConfig

from benefits.enrollment.apps import TransitProcessorAppConfigMixin


class EnrollmentInitConfig(TransitProcessorAppConfigMixin, AppConfig):
    name = "benefits.enrollment_init"
    label = "enrollment_init"
    system_name = "init"
