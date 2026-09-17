from django.apps import AppConfig

from benefits.enrollment.apps import TransitProcessorAppConfigMixin

from .routes import routes


class EnrollmentSwitchioConfig(TransitProcessorAppConfigMixin, AppConfig):
    name = "benefits.enrollment_switchio"
    label = "enrollment_switchio"
    system_name = "switchio"
    enrollment_index_route = routes.ENROLLMENT_SWITCHIO_INDEX
    in_person_enrollment_index_route = routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX
