import logging

from django.core.exceptions import ValidationError
from django.db import models

from benefits.core.models import EnrollmentGroup, SecretNameField, SystemName, TransitProcessorConfig
from benefits.secrets import get_secret_by_name

logger = logging.getLogger(__name__)


class SwitchioGroupIDs:
    # SystemName.name: Switchio group ID
    MEDICARE = "MEDICARE"
    CALFRESH = "LOW_INCOME"
    OLDER_ADULT = "OLDER_ADULT"
    VETERAN = "VETERAN"
    # We have no Switchio agencies with Agency Card flows, but this is needed for testing.
    COURTESY_CARD = "AGENCY_CARD"


class SwitchioConfig(TransitProcessorConfig):
    """Configuration for connecting to Switchio, an entity that applies transit agency fare rules to rider transactions."""

    tokenization_api_key = models.TextField(
        help_text="The API key used to access the Switchio API for tokenization.", default="", blank=True
    )
    tokenization_api_secret_name = SecretNameField(
        help_text="The name of the secret containing the api_secret value used to access the Switchio API for tokenization.",  # noqa: E501
        default="",
        blank=True,
    )
    pto_id = models.PositiveIntegerField(
        help_text="The Public Transport Operator ID to use with the Switchio API for enrollment.",
        default=0,
        blank=True,
    )

    @property
    def tokenization_api_base_url(self):
        return get_secret_by_name("switchio-tokenization-api-base-url")

    @property
    def enrollment_api_base_url(self):
        return get_secret_by_name("switchio-enrollment-api-base-url")

    @property
    def enrollment_api_authorization_header(self):
        return get_secret_by_name("switchio-enrollment-api-authorization-header")

    @property
    def tokenization_api_secret(self):
        secret_field = self._meta.get_field("tokenization_api_secret_name")
        return secret_field.secret_value(self)

    @property
    def client_certificate_data(self):
        """This SwitchioConfig's client certificate as a string."""
        return get_secret_by_name("switchio-client-cert")

    @property
    def ca_certificate_data(self):
        """This SwitchioConfig's CA certificate as a string."""
        return get_secret_by_name("switchio-ca-cert")

    @property
    def private_key_data(self):
        """This SwitchioConfig's private key as a string."""
        return get_secret_by_name("switchio-private-key")

    def clean(self):
        field_errors = {}

        if self.pk and self.transitagency_set and any([agency.active for agency in self.transitagency_set.all()]):
            message = "This field is required when this configuration is referenced by an active transit agency."
            needed = dict(
                tokenization_api_key=self.tokenization_api_key,
                tokenization_api_secret_name=self.tokenization_api_secret_name,
                pto_id=self.pto_id,
            )
            field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

        if field_errors:
            raise ValidationError(field_errors)


class SwitchioGroup(EnrollmentGroup):

    @property
    def group_id(self):
        """Get the Switchio group ID, which is the same for all agencies for a given flow.

        Returns the value of the attribute on SwitchioGroupIDs whose attribute name
        matches the one in SystemName that's used by this group's enrollment flow.
        """
        return getattr(SwitchioGroupIDs, SystemName(self.enrollment_flow.system_name).name, None)

    @staticmethod
    def by_id(id):
        """Get a SwitchioGroup instance by its ID."""
        logger.debug(f"Get {SwitchioGroup.__name__} by id: {id}")
        return SwitchioGroup.objects.get(id=id)
