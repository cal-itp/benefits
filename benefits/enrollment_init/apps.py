from django.apps import AppConfig


class EnrollmentInitConfig(AppConfig):
    name = "benefits.enrollment_init"
    label = "enrollment_init"
    system_name = "init"

    def ready(self):
        from django.apps import apps

        from benefits.enrollment.apps import EnrollmentAppConfig

        enrollment_app_config = apps.get_app_config(EnrollmentAppConfig.label)
        transit_processors = enrollment_app_config.transit_processors
        transit_processors.add(self.system_name, self.module)
