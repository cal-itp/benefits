"""
The oauth application: Implements OAuth-based authentication
"""
from django.apps import AppConfig


class OAuthAppConfig(AppConfig):
    name = "benefits.oauth"
    label = "oauth"
    verbose_name = "Benefits OAuth"

    def ready(self):
        from .client import oauth, register_providers

        register_providers(oauth)
