"""
The core application: Common model definitions.
"""
import logging

from django.db import models
from django.urls import reverse

from jwcrypto import jwk


logger = logging.getLogger(__name__)


class PemData(models.Model):
    """API Certificate or Key in PEM format."""

    id = models.AutoField(primary_key=True)
    text = models.TextField(help_text="The data in utf-8 encoded PEM text format.")
    label = models.TextField(help_text="Human description of the PEM data.")

    def __str__(self):
        return self.label

    @property
    def jwk(self):
        """jwcrypto.jwk.JWK instance from this PemData."""
        pem_bytes = bytes(self.text, "utf-8")
        return jwk.JWK.from_pem(pem_bytes)


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

    # fmt: off
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    api_url = models.TextField()
    api_auth_header = models.TextField()
    api_auth_key = models.TextField()
    eligibility_types = models.ManyToManyField(EligibilityType)
    public_key = models.ForeignKey(PemData, help_text="The Verifier's public key, used to encrypt requests targeted at this Verifier and to verify signed responses from this verifier.", related_name="+", on_delete=models.PROTECT)  # noqa: 503
    jwe_cek_enc = models.TextField(help_text="The JWE-compatible Content Encryption Key (CEK) key-length and mode")
    jwe_encryption_alg = models.TextField(help_text="The JWE-compatible encryption algorithm")
    jws_signing_alg = models.TextField(help_text="The JWS-compatible signing algorithm")
    selection_label = models.TextField()
    selection_label_description = models.TextField(null=True)
    instructions_content_title = models.TextField()
    instructions_item_name = models.TextField()
    instructions_item_description = models.TextField()
    instructions_blurb = models.TextField()
    form_title = models.TextField()
    form_content_title = models.TextField()
    form_blurb = models.TextField()
    form_sub_label = models.TextField()
    form_sub_placeholder = models.TextField()
    form_sub_pattern = models.TextField(null=True, help_text="A regular expression used to validate the 'sub' API field before sending to this verifier")  # noqa: 503
    form_name_label = models.TextField()
    form_name_placeholder = models.TextField()
    form_name_max_length = models.PositiveSmallIntegerField(null=True, help_text="The maximum length accepted for the 'name' API field before sending to this verifier")  # noqa: 503
    # fmt: on

    def __str__(self):
        return self.name

    @property
    def public_jwk(self):
        """jwcrypto.jwk.JWK instance of this Verifier's public key"""
        return self.public_key.jwk


class PaymentProcessor(models.Model):
    """An entity that processes payments for transit agencies."""

    # fmt: off
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    api_base_url = models.TextField()
    api_access_token_endpoint = models.TextField()
    api_access_token_request_key = models.TextField()
    api_access_token_request_val = models.TextField()
    card_tokenize_url = models.TextField()
    card_tokenize_func = models.TextField()
    card_tokenize_env = models.TextField()
    client_cert = models.ForeignKey(PemData, help_text="The certificate used for client certificate authentication to the API.", related_name="+", on_delete=models.PROTECT)  # noqa: 503
    client_cert_private_key = models.ForeignKey(PemData, help_text="The private key, used to sign the certificate.", related_name="+", on_delete=models.PROTECT)  # noqa: 503
    client_cert_root_ca = models.ForeignKey(PemData, help_text="The root CA bundle, used to verify the server.", related_name="+", on_delete=models.PROTECT)  # noqa: 503
    customer_endpoint = models.TextField()
    customers_endpoint = models.TextField()
    group_endpoint = models.TextField()
    # fmt: on

    def __str__(self):
        return self.name


class TransitAgency(models.Model):
    """An agency offering transit service."""

    # fmt: off
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
    private_key = models.ForeignKey(PemData, help_text="The Agency's private key, used to sign tokens created on behalf of this Agency.", related_name="+", on_delete=models.PROTECT)  # noqa: 503
    jws_signing_alg = models.TextField(help_text="The JWS-compatible signing algorithm.")
    # fmt: on

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
        verifier_types = set(eligibility_verifier.eligibility_types.values_list("id", flat=True))
        supported_types = list(agency_types & verifier_types)
        return EligibilityType.get_many(supported_types)

    @property
    def index_url(self):
        """Url to the TransitAgency's landing page."""
        return reverse("core:agency_index", args=[self.slug])

    @property
    def private_jwk(self):
        """jwcrypto.jwk.JWK instance of this Agency's private key"""
        return self.private_key.jwk

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
