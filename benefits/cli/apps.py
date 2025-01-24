"""
The cli application: Command line interface for working with the Cal-ITP Benefits app.
"""

from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    name = "benefits.cli"
    label = "cli"
    verbose_name = "Benefits CLI"
