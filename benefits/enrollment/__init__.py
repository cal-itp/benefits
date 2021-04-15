"""
The enrollment application: Allows user to enroll payment device for benefits.
"""
from django.apps import AppConfig


class EnrollmentAppConfig(AppConfig):
    name = "benefits.enrollment"
    label = "enrollment"
    verbose_name = "Benefits Enrollment"


default_app_config = "benefits.enrollment.EnrollmentAppConfig"
