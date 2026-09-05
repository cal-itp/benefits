from django.core.exceptions import ValidationError
from django.db import models

from benefits.core.models import SecretNameField, TransitProcessorConfig


class InitConfig(TransitProcessorConfig):
    """Configuration for connecting to INIT, an entity that applies transit agency fare rules to rider transactions."""

    tokenization_api_key = models.CharField(help_text="The Collect.js API key used for tokenization.", default="", blank=True)

    registration_base_url = models.URLField(
        help_text="The absolute base url of the MOBILEvario API instance.", default="", blank=True
    )

    registration_username = models.CharField(
        help_text="The username used to authenticate with MOBILEvario.",
        default="",
        blank=True,
        max_length=50,
    )

    registration_password_secret_name = SecretNameField(
        help_text="The name of the secret containing the password used to authenticate with MOBILEvario, "
        "typically: [agency]-init-registration-password",
        default="",
        blank=True,
        max_length=50,
    )

    @property
    def registration_password(self):
        secret_field = self._meta.get_field("registration_password_secret_name")
        return secret_field.secret_value(self)

    def clean(self):
        field_errors = {}

        # TODO: verify the presence of an active transit agency when we're ready to associate the two
        message = "This field is required when this configuration is referenced by an active transit agency."
        needed = dict(
            tokenization_api_key=self.tokenization_api_key,
        )
        field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

        if field_errors:
            raise ValidationError(field_errors)

    class Meta:
        verbose_name = "INIT Config"
