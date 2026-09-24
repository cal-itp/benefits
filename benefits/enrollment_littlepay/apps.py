from django.apps import AppConfig

from benefits.enrollment.apps import TransitProcessorAppConfigMixin

from .routes import routes


class EnrollmentLittlepayConfig(TransitProcessorAppConfigMixin, AppConfig):
    name = "benefits.enrollment_littlepay"
    label = "enrollment_littlepay"
    system_name = "littlepay"
    enrollment_index_route = routes.ENROLLMENT_LITTLEPAY_INDEX
    in_person_enrollment_index_route = routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX
