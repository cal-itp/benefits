"""
The auth application: Allows user to sign in.
"""
from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = "benefits.auth"
    label = "auth"
    verbose_name = "Benefits Auth"


# default_app_config = "benefits.enrollment.AuthAppConfig"
