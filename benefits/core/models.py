"""
The core application: Common model definitions.
"""
import logging

from django.db import models
from django.urls import reverse

import requests


logger = logging.getLogger(__name__)


class PemData(models.Model):
    """API Certificate or Key in PEM format."""

    id = models.AutoField(primary_key=True)
    # Human description of the PEM data
    label = models.TextField()
    # The data in utf-8 encoded PEM text format
    text = models.TextField(null=True)
    # Public URL hosting the utf-8 encoded PEM text
    remote_url = models.TextField(null=True)

    def __str__(self):
        return self.label

    @property
    def data(self):
        if self.text:
            return self.text
        elif self.remote_url:
            self.text = requests.get(self.remote_url).text

        self.save()
        return self.text


class AuthProvider(models.Model):
    """An entity that provides authentication for eligibility verifiers."""

    id = models.AutoField(primary_key=True)
    sign_in_button_label = models.TextField()
    sign_out_button_label = models.TextField()
    client_name = models.TextField()
    client_id = models.TextField()
    authority = models.TextField()
    scope = models.TextField(null=True)
    claim = models.TextField(null=True)


class EligibilityType(models.Model):
    """A single conditional eligibility type."""

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    label = models.TextField()
    group_id = models.TextField()

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


class EligibilityVerifier(models.Model):
    """An entity that verifies eligibility."""

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    api_url = models.TextField(null=True)
    api_auth_header = models.TextField(null=True)
    api_auth_key = models.TextField(null=True)
    eligibility_type = models.ForeignKey(EligibilityType, on_delete=models.PROTECT)
    # public key is used to encrypt requests targeted at this Verifier and to verify signed responses from this verifier
    public_key = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT, null=True)
    # The JWE-compatible Content Encryption Key (CEK) key-length and mode
    jwe_cek_enc = models.TextField(null=True)
    # The JWE-compatible encryption algorithm
    jwe_encryption_alg = models.TextField(null=True)
    # The JWS-compatible signing algorithm
    jws_signing_alg = models.TextField(null=True)
    auth_provider = models.ForeignKey(AuthProvider, on_delete=models.PROTECT, null=True)
    selection_label = models.TextField()
    selection_label_description = models.TextField(null=True)
    start_headline = models.TextField()
    start_sub_headline = models.TextField()
    start_item_name = models.TextField()
    start_item_description = models.TextField()
    start_blurb = models.TextField()
    form_title = models.TextField(null=True)
    form_headline = models.TextField(null=True)
    form_blurb = models.TextField(null=True)
    form_sub_label = models.TextField(null=True)
    form_sub_help_text = models.TextField(null=True)
    form_sub_placeholder = models.TextField(null=True)
    # A regular expression used to validate the 'sub' API field before sending to this verifier
    form_sub_pattern = models.TextField(null=True)
    form_name_label = models.TextField(null=True)
    form_name_help_text = models.TextField(null=True)
    form_name_placeholder = models.TextField(null=True)
    # The maximum length accepted for the 'name' API field before sending to this verifier
    form_name_max_length = models.PositiveSmallIntegerField(null=True)
    unverified_title = models.TextField()
    unverified_headline = models.TextField()
    unverified_blurb = models.TextField()

    def __str__(self):
        return self.name

    @property
    def public_key_data(self):
        """This Verifier's public key as a string."""
        return self.public_key.data

    @property
    def is_auth_required(self):
        """True if this Verifier requires authentication. False otherwise."""
        return self.auth_provider is not None

    @property
    def uses_auth_verification(self):
        """True if this Verifier verifies via the auth provider. False otherwise."""
        return self.is_auth_required and self.auth_provider.scope and self.auth_provider.claim

    @staticmethod
    def by_id(id):
        """Get an EligibilityVerifier instance by its ID."""
        logger.debug(f"Get {EligibilityVerifier.__name__} by id: {id}")
        return EligibilityVerifier.objects.get(id=id)


class PaymentProcessor(models.Model):
    """An entity that processes payments for transit agencies."""

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    api_base_url = models.TextField()
    api_access_token_endpoint = models.TextField()
    api_access_token_request_key = models.TextField()
    api_access_token_request_val = models.TextField()
    card_tokenize_url = models.TextField()
    card_tokenize_func = models.TextField()
    card_tokenize_env = models.TextField()
    # The certificate used for client certificate authentication to the API
    client_cert = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT)
    # The private key, used to sign the certificate
    client_cert_private_key = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT)
    # The root CA bundle, used to verify the server.
    client_cert_root_ca = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT)
    customer_endpoint = models.TextField()
    customers_endpoint = models.TextField()
    group_endpoint = models.TextField()

    def __str__(self):
        return self.name


class TransitAgency(models.Model):
    """An agency offering transit service."""

    id = models.AutoField(primary_key=True)
    slug = models.TextField()
    short_name = models.TextField()
    long_name = models.TextField()
    agency_id = models.TextField()
    merchant_id = models.TextField()
    info_url = models.URLField()
    phone = models.TextField()
    active = models.BooleanField(default=False)
    eligibility_types = models.ManyToManyField(EligibilityType)
    eligibility_verifiers = models.ManyToManyField(EligibilityVerifier)
    payment_processor = models.ForeignKey(PaymentProcessor, on_delete=models.PROTECT)
    # The Agency's private key, used to sign tokens created on behalf of this Agency
    private_key = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT)
    # The public key corresponding to the Agency's private key, used by Eligibility Verification servers to encrypt responses
    public_key = models.ForeignKey(PemData, related_name="+", on_delete=models.PROTECT)
    # The JWS-compatible signing algorithm
    jws_signing_alg = models.TextField()

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

    @property
    def index_url(self):
        """Public-facing URL to the TransitAgency's landing page."""
        return reverse("core:agency_index", args=[self.slug])

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
