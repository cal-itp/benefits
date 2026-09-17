from django.apps import AppConfig

from benefits.enrollment.apps import TransitProcessorAppConfigMixin


class EnrollmentLittlepayConfig(TransitProcessorAppConfigMixin, AppConfig):
    name = "benefits.enrollment_littlepay"
    label = "enrollment_littlepay"
    system_name = "littlepay"
