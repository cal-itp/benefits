from django.core.exceptions import ValidationError
from django.db import models

from benefits.core.models import PemData, SecretNameField, Environment


class SwitchioConfig(models.Model):
    """Configuration for connecting to Switchio, an entity that applies transit agency fare rules to rider transactions."""

    id = models.AutoField(primary_key=True)
    environment = models.TextField(
        choices=Environment,
        help_text="A label to indicate which environment this configuration is for.",
    )
    api_key = models.TextField(help_text="The API key used to access the Switchio API.", default="", blank=True)
    api_secret_name = SecretNameField(
        help_text="The name of the secret containing the api_secret value used to access the Switchio API.",  # noqa: E501
        default="",
        blank=True,
    )
    client_certificate = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        help_text="The client certificate for accessing the Switchio API.",
        null=True,
        blank=True,
        default=None,
    )
    ca_certificate = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        help_text="The CA certificate chain for accessing the Switchio API.",
        null=True,
        blank=True,
        default=None,
    )
    private_key = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        help_text="The private key for accessing the Switchio API.",
        null=True,
        blank=True,
        default=None,
    )

    @property
    def api_base_url(self):
        if self.environment == Environment.QA.value:
            return ""
        elif self.environment == Environment.PROD.value:
            return ""
        else:
            raise ValueError(f"Unexpected value for environment: {self.environment}")

    @property
    def api_secret(self):
        secret_field = self._meta.get_field("api_secret_name")
        return secret_field.secret_value(self)

    def clean(self, agency=None):
        field_errors = {}

        if agency is not None:
            used_by_active_agency = agency.active
        elif self.pk is not None:
            used_by_active_agency = any((agency.active for agency in self.transitagency_set.all()))
        else:
            used_by_active_agency = False

        if used_by_active_agency:
            message = "This field is required when this configuration is referenced by an active transit agency."
            needed = dict(
                api_key=self.api_key,
                api_secret_name=self.api_secret_name,
                client_certificate=self.client_certificate,
                ca_certificate=self.ca_certificate,
                private_key=self.private_key,
            )
            field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

        if field_errors:
            raise ValidationError(field_errors)

    def __str__(self):
        environment_label = Environment(self.environment).label if self.environment else "unknown"
        return f"{environment_label}"
