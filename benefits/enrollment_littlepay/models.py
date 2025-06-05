from django.core.exceptions import ValidationError
from django.db import models

from benefits.core import context as core_context
from benefits.core.models import SecretNameField, Environment
from benefits.secrets import get_secret_by_name


class LittlepayConfig(models.Model):
    """Configuration for connecting to Littlepay, an entity that applies transit agency fare rules to rider transactions."""

    id = models.AutoField(primary_key=True)
    environment = models.TextField(
        choices=Environment,
        help_text="A label to indicate which environment this configuration is for.",
    )
    agency_slug = models.SlugField(
        choices=core_context.AgencySlug,
        help_text="A label to indicate which agency this configuration is for. Note: the field that controls which configuration an agency actually uses is on the TransitAgency model.",  # noqa
    )
    audience = models.TextField(
        help_text="This agency's audience value used to access the TransitProcessor's API.", default="", blank=True
    )
    client_id = models.TextField(
        help_text="This agency's client_id value used to access the TransitProcessor's API.", default="", blank=True
    )
    client_secret_name = SecretNameField(
        help_text="The name of the secret containing this agency's client_secret value used to access the TransitProcessor's API.",  # noqa: E501
        default="",
        blank=True,
    )

    @property
    def api_base_url(self):
        if self.environment == Environment.QA.value:
            return get_secret_by_name("littlepay-qa-api-base-url")
        elif self.environment == Environment.PROD.value:
            return get_secret_by_name("littlepay-prod-api-base-url")
        else:
            raise ValueError(f"Unexpected value for environment: {self.environment}")

    @property
    def client_secret(self):
        secret_field = self._meta.get_field("client_secret_name")
        return secret_field.secret_value(self)

    def clean(self):
        field_errors = {}

        if hasattr(self, "transitagency") and self.transitagency.active:
            message = "This field is required when this configuration is referenced by an active transit agency."
            needed = dict(audience=self.audience, client_id=self.client_id, client_secret_name=self.client_secret_name)
            field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

        if field_errors:
            raise ValidationError(field_errors)

    def __str__(self):
        environment_label = Environment(self.environment).label if self.environment else "unknown"
        agency_slug = self.agency_slug if self.agency_slug else "(no agency)"
        return f"({environment_label}) {agency_slug}"
