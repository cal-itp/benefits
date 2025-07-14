from django.core.exceptions import ValidationError
from django.db import models

from benefits.core.models import SecretNameField, Environment, EnrollmentGroup, TransitProcessorConfig
from benefits.secrets import get_secret_by_name


class LittlepayConfig(TransitProcessorConfig):
    """Configuration for connecting to Littlepay, an entity that applies transit agency fare rules to rider transactions."""

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


class LittlepayGroup(EnrollmentGroup):
    group_id = models.UUIDField(default=None, blank=True, help_text="The ID of the Littlepay group for user enrollment.")
