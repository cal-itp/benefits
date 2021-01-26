"""
The core application: Common model definitions.
"""
from django.db import models
from django.urls import reverse

from jwcrypto import jwk


def pem_to_jwk(pem):
    """jwcrypto.jwk.JWK instance of a key in PEM format"""
    if not isinstance(pem, bytes):
        pem = bytes(str(pem), "utf-8")
    return jwk.JWK.from_pem(pem)


class DiscountProvider(models.Model):
    """An entity that provides transit discounts."""

    name = models.TextField()
    api_base_url = models.TextField()
    api_access_token_endpoint = models.TextField()
    api_access_token_request_key = models.TextField()
    api_access_token_request_val = models.TextField()
    card_tokenize_url = models.TextField()
    card_tokenize_func = models.TextField()
    card_tokenize_env = models.TextField()
    client_cert_pem = models.TextField(
        help_text="A certificate in PEM format, used for client certificate authentication to this Provider's API."
    )
    client_cert_private_key_pem = models.TextField(
        help_text="The private key in PEM format used to sign the certificate."
    )
    client_cert_root_ca_pem = models.TextField(
        help_text="The root CA bundle in PEM format used to verify the Provider's server."
    )
    customer_endpoint = models.TextField()
    customers_endpoint = models.TextField()

    def __str__(self):
        return self.name


class EligibilityType(models.Model):
    """A single conditional eligibility type."""

    name = models.TextField()
    label = models.TextField()
    group_id = models.TextField()

    def __str__(self):
        return self.label


class EligibilityVerifier(models.Model):
    """An entity that verifies eligibility."""

    name = models.TextField()
    api_url = models.TextField()
    api_auth_header = models.TextField()
    api_auth_key = models.TextField()
    eligibility_types = models.ManyToManyField(EligibilityType)
    public_key_pem = models.TextField(
        help_text="The Verifier's public key in PEM format, used to encrypt requests targeted at this Verifier \
            and to verify signed responses from this verifier."
    )
    jwe_cek_enc = models.TextField(
        help_text="The JWE-compatible Content Encryption Key (CEK) key-length and mode"
    )
    jwe_encryption_alg = models.TextField(
        help_text="The JWE-compatible encryption algorithm"
    )
    jws_signing_alg = models.TextField(
        help_text="The JWS-compatible signing algorithm"
    )

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

    slug = models.TextField()
    short_name = models.TextField()
    long_name = models.TextField()
    agency_id = models.TextField()
    merchant_id = models.TextField()
    logo_url = models.URLField()
    street_address1 = models.TextField()
    street_address2 = models.TextField(blank=True)
    city = models.TextField()
    zip_code = models.TextField()
    country_code = models.TextField()
    phone = models.TextField()
    active = models.BooleanField(default=False)
    eligibility_types = models.ManyToManyField(EligibilityType)
    eligibility_verifiers = models.ManyToManyField(EligibilityVerifier)
    discount_provider = models.ForeignKey(DiscountProvider, on_delete=models.PROTECT)
    private_key_pem = models.TextField(
        help_text="The Agency's private key in PEM format, used to sign tokens created on behalf of this Agency."
    )
    jws_signing_alg = models.TextField(
        help_text="The JWS-compatible signing algorithm."
    )

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
        return TransitAgency.objects.get(id=id)

    @staticmethod
    def by_slug(slug):
        """Get a TransitAgency instance by its slug."""
        return TransitAgency.objects.filter(slug=slug).first()

    @staticmethod
    def all_active():
        """Get all TransitAgency instances marked active."""
        return TransitAgency.objects.filter(active=True)
