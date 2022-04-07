"""
The auth application: Allows user to sign in.
"""
from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = "benefits.authn"
    label = "authn"
    verbose_name = "Benefits Auth"


# default_app_config = "benefits.enrollment.AuthAppConfig"
