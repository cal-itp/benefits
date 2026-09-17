from django.apps import AppConfig


class EnrollmentSwitchioConfig(AppConfig):
    name = "benefits.enrollment_switchio"
    label = "enrollment_switchio"
    system_name = "switchio"

    def ready(self):
        from django.apps import apps

        from benefits.enrollment.apps import EnrollmentAppConfig

        enrollment_app_config = apps.get_app_config(EnrollmentAppConfig.label)
        transit_processors = enrollment_app_config.transit_processors
        transit_processors.add(self.system_name, self.module)
