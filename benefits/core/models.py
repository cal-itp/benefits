"""
The core application: Common model definitions.
"""
import logging

from django.db import models
from django.urls import reverse

from jwcrypto import jwk


logger = logging.getLogger(__name__)


def pem_to_jwk(pem):
    """jwcrypto.jwk.JWK instance of a key in PEM format"""
    if not isinstance(pem, bytes):
        pem = bytes(str(pem), "utf-8")
    return jwk.JWK.from_pem(pem)


class BenefitsProvider(models.Model):
    """An entity that provides transit benefits."""

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
    client_cert_pem = models.TextField(help_text="A certificate in PEM format, used for client certificate authentication to this Provider's API.")  # noqa: 503
    client_cert_private_key_pem = models.TextField(help_text="The private key in PEM format used to sign the certificate.")
    client_cert_root_ca_pem = models.TextField(help_text="The root CA bundle in PEM format used to verify the Provider's server.")  # noqa: 503
    customer_endpoint = models.TextField()
    customers_endpoint = models.TextField()
    group_endpoint = models.TextField()
    # fmt: on

    def __str__(self):
        return self.name


class EligibilityType(models.Model):
    """A single conditional eligibility type."""

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    label = models.TextField()
    group_id = models.TextField()

    def __str__(self):
        return self.label

    @staticmethod
    def by_name(name):
        """Get an EligibilityType instance by its name."""
        logger.debug(f"Get {EligibilityType.__name__} by name: {name}")
        return EligibilityType.objects.get(name=name)


class EligibilityVerifier(models.Model):
    """An entity that verifies eligibility."""

    # fmt: off
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    api_url = models.TextField()
    api_auth_header = models.TextField()
    api_auth_key = models.TextField()
    eligibility_types = models.ManyToManyField(EligibilityType)
    public_key_pem = models.TextField(help_text="The Verifier's public key in PEM format, used to encrypt requests targeted at this Verifier and to verify signed responses from this verifier.")  # noqa: 503
    jwe_cek_enc = models.TextField(help_text="The JWE-compatible Content Encryption Key (CEK) key-length and mode")
    jwe_encryption_alg = models.TextField(help_text="The JWE-compatible encryption algorithm")
    jws_signing_alg = models.TextField(help_text="The JWS-compatible signing algorithm")
    # fmt: on

    def __str__(self):
        return self.name

    @property
    def eligibility_set(self):
        """Set of eligibility_type names"""
        return set(self.eligibility_types.values_list("name", flat=True))

    @property
    def public_jwk(self):
        """jwcrypto.jwk.JWK instance of this Verifier's public key"""
        return pem_to_jwk(self.public_key_pem)


class TransitAgency(models.Model):
    """An agency offering transit service."""

    # fmt: off
    id = models.AutoField(primary_key=True)
    slug = models.TextField()
    short_name = models.TextField()
    long_name = models.TextField()
    agency_id = models.TextField()
    merchant_id = models.TextField()
    logo_url = models.URLField()
    phone = models.TextField()
    active = models.BooleanField(default=False)
    eligibility_types = models.ManyToManyField(EligibilityType)
    eligibility_verifier = models.ForeignKey(EligibilityVerifier, on_delete=models.PROTECT)
    benefits_provider = models.ForeignKey(BenefitsProvider, on_delete=models.PROTECT)
    private_key_pem = models.TextField(help_text="The Agency's private key in PEM format, used to sign tokens created on behalf of this Agency.")  # noqa: 503
    jws_signing_alg = models.TextField(help_text="The JWS-compatible signing algorithm.")
    # fmt: on

    def __str__(self):
        return self.long_name

    @property
    def eligibility_set(self):
        """Set of eligibility_type names"""
        return set(self.eligibility_types.values_list("name", flat=True))

    @property
    def index_url(self):
        """Url to the TransitAgency's landing page."""
        return reverse("core:agency_index", args=[self.slug])

    @property
    def private_jwk(self):
        """jwcrypto.jwk.JWK instance of this Agency's private key"""
        return pem_to_jwk(self.private_key_pem)

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
