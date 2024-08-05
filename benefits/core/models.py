"""
The core application: Common model definitions.
"""

from functools import cached_property
import importlib
import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

import requests

from benefits.secrets import NAME_VALIDATOR, get_secret_by_name


logger = logging.getLogger(__name__)


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


class PemData(models.Model):
    """API Certificate or Key in PEM format."""

    id = models.AutoField(primary_key=True)
    # Human description of the PEM data
    label = models.TextField()
    # The name of a secret with data in utf-8 encoded PEM text format
    text_secret_name = SecretNameField(null=True, blank=True)
    # Public URL hosting the utf-8 encoded PEM text
    remote_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.label

    @cached_property
    def data(self):
        """
        Attempts to get data from `remote_url` or `text_secret_name`, with the latter taking precendence if both are defined.
        """
        remote_data = None
        secret_data = None

        if self.remote_url:
            remote_data = requests.get(self.remote_url, timeout=settings.REQUESTS_TIMEOUT).text
        if self.text_secret_name:
            try:
                secret_data = get_secret_by_name(self.text_secret_name)
            except Exception:
                secret_data = None

        return secret_data if secret_data is not None else remote_data


class ClaimsProvider(models.Model):
    """An entity that provides claims for eligibility verification."""

    id = models.AutoField(primary_key=True)
    sign_out_button_template = models.TextField(null=True, blank=True, help_text="Template that renders sign-out button")
    sign_out_link_template = models.TextField(null=True, blank=True, help_text="Template that renders sign-out link")
    client_name = models.TextField(help_text="Unique identifier used to register this claims provider with Authlib registry")
    client_id_secret_name = SecretNameField(
        help_text="The name of the secret containing the client ID for this claims provider"
    )
    authority = models.TextField(help_text="The fully qualified HTTPS domain name for an OAuth authority server")
    scope = models.TextField(
        null=True,
        blank=True,
        help_text="A space-separated list of identifiers used to specify what access privileges are being requested",
    )
    claim = models.TextField(
        null=True, blank=True, help_text="The name of the claim (name/value pair) that is used to verify eligibility"
    )
    scheme = models.TextField(help_text="The authentication scheme to use")

    @property
    def supports_claims_verification(self):
        return bool(self.scope) and bool(self.claim)

    @property
    def supports_sign_out(self):
        return bool(self.sign_out_button_template) or bool(self.sign_out_link_template)

    @property
    def client_id(self):
        return get_secret_by_name(self.client_id_secret_name)

    def __str__(self) -> str:
        return self.client_name


class EligibilityType(models.Model):
    """A single conditional eligibility type."""

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    label = models.TextField()
    group_id = models.TextField()
    supports_expiration = models.BooleanField(default=False)
    expiration_days = models.PositiveSmallIntegerField(null=True, blank=True)
    expiration_reenrollment_days = models.PositiveSmallIntegerField(null=True, blank=True)
    enrollment_index_template = models.TextField(default="enrollment/index.html")
    reenrollment_error_template = models.TextField(null=True, blank=True)
    enrollment_success_template = models.TextField(default="enrollment/success.html")

    def __str__(self):
        return self.label

    @staticmethod
    def get(id):
        """Get an EligibilityType instance by its id."""
        logger.debug(f"Get {EligibilityType.__name__} by id: {id}")
        return EligibilityType.objects.get(pk=id)

    @staticmethod
    def get_many(ids):
        """Get a list of EligibilityType instances from a list of ids."""
        logger.debug(f"Get {EligibilityType.__name__} list by ids: {ids}")
        return EligibilityType.objects.filter(id__in=ids)

    @staticmethod
    def get_names(eligibility_types):
        """Convert a list of EligibilityType to a list of their names"""
        if isinstance(eligibility_types, EligibilityType):
            eligibility_types = [eligibility_types]
        return [t.name for t in eligibility_types if isinstance(t, EligibilityType)]

    def clean(self):
        supports_expiration = self.supports_expiration
        expiration_days = self.expiration_days
        expiration_reenrollment_days = self.expiration_reenrollment_days
        reenrollment_error_template = self.reenrollment_error_template

        if supports_expiration:
            errors = {}
            message = "When support_expiration is True, this value must be greater than 0."
            if expiration_days is None or expiration_days <= 0:
                errors.update(expiration_days=ValidationError(message))
            if expiration_reenrollment_days is None or expiration_reenrollment_days <= 0:
                errors.update(expiration_reenrollment_days=ValidationError(message))
            if reenrollment_error_template is None:
                errors.update(reenrollment_error_template=ValidationError("Required when supports expiration is True."))

            if errors:
                raise ValidationError(errors)


class EligibilityVerifier(models.Model):
    """An entity that verifies eligibility."""

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    display_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=False)
    api_url = models.TextField(null=True, blank=True)
    api_auth_header = models.TextField(null=True, blank=True)
    api_auth_key_secret_name = SecretNameField(null=True, blank=True)
    eligibility_type = models.ForeignKey(EligibilityType, on_delete=models.PROTECT)
    # public key is used to encrypt requests targeted at this Verifier and to verify signed responses from this verifier
    public_key = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT, null=True, blank=True)
    # The JWE-compatible Content Encryption Key (CEK) key-length and mode
    jwe_cek_enc = models.TextField(null=True, blank=True)
    # The JWE-compatible encryption algorithm
    jwe_encryption_alg = models.TextField(null=True, blank=True)
    # The JWS-compatible signing algorithm
    jws_signing_alg = models.TextField(null=True, blank=True)
    claims_provider = models.ForeignKey(ClaimsProvider, on_delete=models.PROTECT, null=True, blank=True)
    selection_label_template = models.TextField()
    start_template = models.TextField(null=True, blank=True)
    # reference to a form class used by this Verifier, e.g. benefits.app.forms.FormClass
    form_class = models.TextField(null=True, blank=True)
    unverified_template = models.TextField(default="eligibility/unverified.html")
    help_template = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.name

    @property
    def api_auth_key(self):
        if self.api_auth_key_secret_name is not None:
            return get_secret_by_name(self.api_auth_key_secret_name)
        else:
            return None

    @property
    def public_key_data(self):
        """This Verifier's public key as a string."""
        return self.public_key.data

    @property
    def uses_claims_verification(self):
        """True if this Verifier verifies via the claims provider. False otherwise."""
        return self.claims_provider is not None and self.claims_provider.supports_claims_verification

    def form_instance(self, *args, **kwargs):
        """Return an instance of this verifier's form, or None."""
        if not bool(self.form_class):
            return None

        # inspired by https://stackoverflow.com/a/30941292
        module_name, class_name = self.form_class.rsplit(".", 1)
        FormClass = getattr(importlib.import_module(module_name), class_name)

        return FormClass(*args, **kwargs)

    @staticmethod
    def by_id(id):
        """Get an EligibilityVerifier instance by its ID."""
        logger.debug(f"Get {EligibilityVerifier.__name__} by id: {id}")
        return EligibilityVerifier.objects.get(id=id)


class TransitProcessor(models.Model):
    """An entity that applies transit agency fare rules to rider transactions."""

    id = models.AutoField(primary_key=True)
    name = models.TextField(help_text="Primary internal display name for this TransitProcessor instance, e.g. in the Admin.")
    api_base_url = models.TextField(help_text="The absolute base URL for the TransitProcessor's API, including https://.")
    card_tokenize_url = models.TextField(
        help_text="The absolute URL for the client-side card tokenization library provided by the TransitProcessor."
    )
    card_tokenize_func = models.TextField(
        help_text="The function from the card tokenization library to call on the client to initiate the process."
    )
    card_tokenize_env = models.TextField(help_text="The environment in which card tokenization is occurring.")

    def __str__(self):
        return self.name


class TransitAgency(models.Model):
    """An agency offering transit service."""

    id = models.AutoField(primary_key=True)
    slug = models.TextField()
    short_name = models.TextField()
    long_name = models.TextField()
    agency_id = models.TextField()
    info_url = models.URLField()
    phone = models.TextField()
    active = models.BooleanField(default=False)
    eligibility_types = models.ManyToManyField(EligibilityType)
    eligibility_verifiers = models.ManyToManyField(EligibilityVerifier)
    transit_processor = models.ForeignKey(TransitProcessor, on_delete=models.PROTECT)
    transit_processor_client_id = models.TextField(
        help_text="This agency's client_id value used to access the TransitProcessor's API.", default=""
    )
    transit_processor_client_secret_name = SecretNameField(
        help_text="The name of the secret containing this agency's client_secret value used to access the TransitProcessor's API.",  # noqa: E501
        default="",
    )
    transit_processor_audience = models.TextField(
        help_text="This agency's audience value used to access the TransitProcessor's API.", default=""
    )
    # The Agency's private key, used to sign tokens created on behalf of this Agency
    private_key = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT)
    # The public key corresponding to the Agency's private key, used by Eligibility Verification servers to encrypt responses
    public_key = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT)
    # The JWS-compatible signing algorithm
    jws_signing_alg = models.TextField()
    index_template = models.TextField()
    eligibility_index_template = models.TextField()

    def __str__(self):
        return self.long_name

    def get_type_id(self, name):
        """Get the id of the EligibilityType identified by the given name for this agency."""
        eligibility = self.eligibility_types.all().filter(name=name)
        if eligibility.count() == 1:
            return eligibility[0].id
        else:
            raise Exception("name does not correspond to a single eligibility type for agency")

    def supports_type(self, eligibility_type):
        """True if the eligibility_type is one of this agency's types. False otherwise."""
        return isinstance(eligibility_type, EligibilityType) and eligibility_type in self.eligibility_types.all()

    def types_to_verify(self, eligibility_verifier):
        """List of eligibility types to verify for this agency."""
        # compute set intersection of agency and verifier type ids
        agency_types = set(self.eligibility_types.values_list("id", flat=True))
        verifier_types = {eligibility_verifier.eligibility_type.id}
        supported_types = list(agency_types & verifier_types)
        return EligibilityType.get_many(supported_types)

    def type_names_to_verify(self, verifier):
        """List of names of the eligibility types to check for this agency."""
        return EligibilityType.get_names(self.types_to_verify(verifier))

    @property
    def index_url(self):
        """Public-facing URL to the TransitAgency's landing page."""
        return reverse("core:agency_index", args=[self.slug])

    @property
    def eligibility_index_url(self):
        """Public facing URL to the TransitAgency's eligibility page."""
        return reverse("eligibility:agency_index", args=[self.slug])

    @property
    def public_key_url(self):
        """Public-facing URL to the TransitAgency's public key."""
        return reverse("core:agency_public_key", args=[self.slug])

    @property
    def private_key_data(self):
        """This Agency's private key as a string."""
        return self.private_key.data

    @property
    def public_key_data(self):
        """This Agency's public key as a string."""
        return self.public_key.data

    @property
    def active_verifiers(self):
        """This Agency's eligibility verifiers that are active."""
        return self.eligibility_verifiers.filter(active=True)

    @property
    def transit_processor_client_secret(self):
        return get_secret_by_name(self.transit_processor_client_secret_name)

    @staticmethod
    def by_id(id):
        """Get a TransitAgency instance by its ID."""
        logger.debug(f"Get {TransitAgency.__name__} by id: {id}")
        return TransitAgency.objects.get(id=id)

    @staticmethod
    def by_slug(slug):
        """Get a TransitAgency instance by its slug."""
        logger.debug(f"Get {TransitAgency.__name__} by slug: {slug}")
        return TransitAgency.objects.filter(slug=slug).first()

    @staticmethod
    def all_active():
        """Get all TransitAgency instances marked active."""
        logger.debug(f"Get all active {TransitAgency.__name__}")
        return TransitAgency.objects.filter(active=True)
