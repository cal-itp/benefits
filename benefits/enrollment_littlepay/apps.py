from django.apps import AppConfig


class EnrollmentLittlepayConfig(AppConfig):
    name = "benefits.enrollment_littlepay"
    label = "enrollment_littlepay"
    system_name = "littlepay"

    def ready(self):
        from django.apps import apps

        from benefits.enrollment.apps import EnrollmentAppConfig

        enrollment_app_config = apps.get_app_config(EnrollmentAppConfig.label)
        transit_processors = enrollment_app_config.transit_processors
        transit_processors.add(self.system_name, self.module)
