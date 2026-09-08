from django.core.exceptions import ValidationError
from django.db import models

from benefits.core.models import EnrollmentGroup, SecretNameField, TransitProcessorConfig


class InitConfig(TransitProcessorConfig):
    """Configuration for connecting to INIT, an entity that applies transit agency fare rules to rider transactions."""

    tokenization_api_key = models.CharField(help_text="The Collect.js API key used for tokenization.", default="", blank=True)

    registration_api_base_url = models.URLField(
        help_text="The absolute base url of the MOBILEvario API instance.", default="", blank=True
    )

    registration_api_username = models.CharField(
        help_text="The username used to authenticate with MOBILEvario.",
        default="",
        blank=True,
        max_length=50,
    )

    registration_api_password_secret_name = SecretNameField(
        help_text="The name of the secret containing the password used to authenticate with MOBILEvario, typically: [agency]-init-registration-api-password",  # noqa: E501
        default="",
        blank=True,
    )

    @property
    def registration_api_password(self):
        secret_field = self._meta.get_field("registration_api_password_secret_name")
        return secret_field.secret_value(self)

    def clean(self):
        field_errors = {}

        if self.pk and self.transitagency_set and any([agency.active for agency in self.transitagency_set.all()]):

            message = "This field is required when this configuration is referenced by an active transit agency."
            needed = dict(
                tokenization_api_key=self.tokenization_api_key,
                registration_api_base_url=self.registration_api_base_url,
                registration_api_username=self.registration_api_username,
                registration_api_password_secret_name=self.registration_api_password_secret_name,
            )
            field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

        if field_errors:
            raise ValidationError(field_errors)

    class Meta:
        verbose_name = "INIT config"


class InitGroup(EnrollmentGroup):
    group_id = models.PositiveIntegerField(
        default=None, blank=True, help_text="The ID of the INIT FareCategory for user enrollment."
    )

    class Meta:
        verbose_name = "INIT group"
