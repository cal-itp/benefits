import logging
from functools import cached_property
from pathlib import Path

import requests
from django import template
from django.conf import settings
from django.db import models

from benefits.secrets import NAME_VALIDATOR, get_secret_by_name

logger = logging.getLogger(__name__)


class Environment(models.TextChoices):
    QA = "qa", "QA"
    ACC = "acc", "Acceptance"
    PROD = "prod", "Production"


def template_path(template_name: str) -> Path:
    """Get a `pathlib.Path` for the named template, or None if it can't be found.

    A `template_name` is the app-local name, e.g. `enrollment/success.html`.

    Adapted from https://stackoverflow.com/a/75863472.
    """
    if template_name:
        for engine in template.engines.all():
            for loader in engine.engine.template_loaders:
                for origin in loader.get_template_sources(template_name):
                    path = Path(origin.name)
                    if path.exists() and path.is_file():
                        return path
    return None


class SecretNameField(models.SlugField):
    """Field that stores the name of a secret held in a secret store.

    The secret value itself MUST NEVER be stored in this field.
    """

    description = """Field that stores the name of a secret held in a secret store.

    Secret names must be between 1-127 alphanumeric ASCII characters or hyphen characters.

    The secret value itself MUST NEVER be stored in this field.
    """

    def __init__(self, *args, **kwargs):
        kwargs["validators"] = [NAME_VALIDATOR]
        # although the validator also checks for a max length of 127
        # this setting enforces the length at the database column level as well
        kwargs["max_length"] = 127
        # the default is False, but this is more explicit
        kwargs["allow_unicode"] = False
        super().__init__(*args, **kwargs)

    def secret_value(self, instance):
        """Get the secret value from the secret store."""
        secret_name = getattr(instance, self.attname)
        return get_secret_by_name(secret_name)


class PemData(models.Model):
    """API Certificate or Key in PEM format."""

    id = models.AutoField(primary_key=True)
    label = models.TextField(help_text="Human description of the PEM data")
    text_secret_name = SecretNameField(
        default="", blank=True, help_text="The name of a secret with data in utf-8 encoded PEM text format"
    )
    remote_url = models.TextField(default="", blank=True, help_text="Public URL hosting the utf-8 encoded PEM text")

    def __str__(self):
        return self.label

    @cached_property
    def data(self):
        """
        Attempts to get data from `remote_url` or `text_secret_name`, with the latter taking precendence if both are defined.
        """
        remote_data = None
        secret_data = None

        if self.text_secret_name:
            try:
                secret_field = self._meta.get_field("text_secret_name")
                secret_data = secret_field.secret_value(self)
            except Exception:
                secret_data = None

        if secret_data is None and self.remote_url:
            remote_data = requests.get(self.remote_url, timeout=settings.REQUESTS_TIMEOUT).text

        return secret_data if secret_data is not None else remote_data
