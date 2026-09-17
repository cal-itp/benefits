from django.apps import AppConfig

from benefits.enrollment.apps import TransitProcessorAppConfigMixin

from .routes import routes


class EnrollmentInitConfig(TransitProcessorAppConfigMixin, AppConfig):
    name = "benefits.enrollment_init"
    label = "enrollment_init"
    system_name = "init"
    enrollment_index_route = routes.ENROLLMENT_INIT_INDEX

    @property
    def system_name_for_display(self):
        return self.system_name.upper()
