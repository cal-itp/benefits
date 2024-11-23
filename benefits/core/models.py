"""
The core application: Common model definitions.
"""

from functools import cached_property
import importlib
import logging
import os
from pathlib import Path
import uuid

from django import template
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, User
from django.db import models
from django.urls import reverse
from django.utils import timezone

import requests

from benefits.routes import routes
from benefits.secrets import NAME_VALIDATOR, get_secret_by_name
from multiselectfield import MultiSelectField


logger = logging.getLogger(__name__)


def template_path(template_name: str) -> Path:
    """Get a `pathlib.Path` for the named template, or None if it can't be found.

    A `template_name` is the app-local name, e.g. `enrollment/success.html`.

    Adapted from https://stackoverflow.com/a/75863472.
    """
    if template_name:
        for engine in template.engines.all():
            for loader in engine.engine.template_loaders:
                for origin in loader.get_template_sources(template_name):
                    path = Path(origin.name)
                    if path.exists() and path.is_file():
                        return path
    return None


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
    text_secret_name = SecretNameField(default="", blank=True)
    # Public URL hosting the utf-8 encoded PEM text
    remote_url = models.TextField(default="", blank=True)

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
    sign_out_button_template = models.TextField(default="", blank=True, help_text="Template that renders sign-out button")
    sign_out_link_template = models.TextField(default="", blank=True, help_text="Template that renders sign-out link")
    client_name = models.TextField(help_text="Unique identifier used to register this claims provider with Authlib registry")
    client_id_secret_name = SecretNameField(
        help_text="The name of the secret containing the client ID for this claims provider"
    )
    authority = models.TextField(help_text="The fully qualified HTTPS domain name for an OAuth authority server")
    scheme = models.TextField(help_text="The authentication scheme to use")

    @property
    def supports_sign_out(self):
        return bool(self.sign_out_button_template) or bool(self.sign_out_link_template)

    @property
    def client_id(self):
        return get_secret_by_name(self.client_id_secret_name)

    def __str__(self) -> str:
        return self.client_name


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
    portal_url = models.TextField(
        default="",
        blank=True,
        help_text="The absolute base URL for the TransitProcessor's control portal, including https://.",
    )

    def __str__(self):
        return self.name


def _agency_logo(instance, filename, size):
    base, ext = os.path.splitext(filename)
    return f"agencies/{instance.slug}-{size}" + ext


def agency_logo_small(instance, filename):
    return _agency_logo(instance, filename, "sm")


def agency_logo_large(instance, filename):
    return _agency_logo(instance, filename, "lg")


class TransitAgency(models.Model):
    """An agency offering transit service."""

    id = models.AutoField(primary_key=True)
    active = models.BooleanField(default=False, help_text="Determines if this Agency is enabled for users")
    slug = models.SlugField(help_text="Used for URL navigation for this agency, e.g. the agency homepage url is /{slug}")
    short_name = models.TextField(
        default="", blank=True, help_text="The user-facing short name for this agency. Often an uppercase acronym."
    )
    long_name = models.TextField(
        default="",
        blank=True,
        help_text="The user-facing long name for this agency. Often the short_name acronym, spelled out.",
    )
    info_url = models.URLField(
        default="",
        blank=True,
        help_text="URL of a website/page with more information about the agency's discounts",
    )
    phone = models.TextField(default="", blank=True, help_text="Agency customer support phone number")
    index_template_override = models.TextField(
        help_text="Override the default template used for this agency's landing page",
        blank=True,
        default="",
    )
    eligibility_index_template_override = models.TextField(
        help_text="Override the default template used for this agency's eligibility landing page",
        blank=True,
        default="",
    )
    eligibility_api_id = models.TextField(
        help_text="The identifier for this agency used in Eligibility API calls.",
        blank=True,
        default="",
    )
    eligibility_api_private_key = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        help_text="Private key used to sign Eligibility API tokens created on behalf of this Agency.",
        null=True,
        blank=True,
        default=None,
    )
    eligibility_api_public_key = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        help_text="Public key corresponding to the agency's private key, used by Eligibility Verification servers to encrypt responses.",  # noqa: E501
        null=True,
        blank=True,
        default=None,
    )
    transit_processor = models.ForeignKey(
        TransitProcessor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        help_text="This agency's TransitProcessor.",
    )
    transit_processor_audience = models.TextField(
        help_text="This agency's audience value used to access the TransitProcessor's API.", default="", blank=True
    )
    transit_processor_client_id = models.TextField(
        help_text="This agency's client_id value used to access the TransitProcessor's API.", default="", blank=True
    )
    transit_processor_client_secret_name = SecretNameField(
        help_text="The name of the secret containing this agency's client_secret value used to access the TransitProcessor's API.",  # noqa: E501
        default="",
        blank=True,
    )
    staff_group = models.OneToOneField(
        Group,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        help_text="The group of users associated with this TransitAgency.",
        related_name="transit_agency",
    )
    sso_domain = models.TextField(
        blank=True,
        default="",
        help_text="The email domain of users to automatically add to this agency's staff group upon login.",
    )
    customer_service_group = models.OneToOneField(
        Group,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        help_text="The group of users who are allowed to do in-person eligibility verification and enrollment.",
        related_name="+",
    )
    logo_large = models.ImageField(
        default="",
        blank=True,
        upload_to=agency_logo_large,
        help_text="The large version of the transit agency's logo.",
    )
    logo_small = models.ImageField(
        default="",
        blank=True,
        upload_to=agency_logo_small,
        help_text="The small version of the transit agency's logo.",
    )

    def __str__(self):
        return self.long_name

    @property
    def index_template(self):
        return self.index_template_override or f"core/index--{self.slug}.html"

    @property
    def index_url(self):
        """Public-facing URL to the TransitAgency's landing page."""
        return reverse(routes.AGENCY_INDEX, args=[self.slug])

    @property
    def eligibility_index_template(self):
        return self.eligibility_index_template_override or f"eligibility/index--{self.slug}.html"

    @property
    def eligibility_index_url(self):
        """Public facing URL to the TransitAgency's eligibility page."""
        return reverse(routes.AGENCY_ELIGIBILITY_INDEX, args=[self.slug])

    @property
    def eligibility_api_private_key_data(self):
        """This Agency's private key as a string."""
        return self.eligibility_api_private_key.data

    @property
    def eligibility_api_public_key_data(self):
        """This Agency's public key as a string."""
        return self.eligibility_api_public_key.data

    @property
    def transit_processor_client_secret(self):
        return get_secret_by_name(self.transit_processor_client_secret_name)

    @property
    def enrollment_flows(self):
        return self.enrollmentflow_set

    def clean(self):
        field_errors = {}
        template_errors = []

        if self.active:
            message = "This field is required for active transit agencies."
            needed = dict(
                short_name=self.short_name,
                long_name=self.long_name,
                phone=self.phone,
                info_url=self.info_url,
                logo_large=self.logo_large,
                logo_small=self.logo_small,
            )
            if self.transit_processor:
                needed.update(
                    dict(
                        transit_processor_audience=self.transit_processor_audience,
                        transit_processor_client_id=self.transit_processor_client_id,
                        transit_processor_client_secret_name=self.transit_processor_client_secret_name,
                    )
                )
            field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

            # since templates are calculated from the pattern or the override field
            # we can't add a field-level validation error
            # so just create directly for a missing template
            for t in [self.index_template, self.eligibility_index_template]:
                if not template_path(t):
                    template_errors.append(ValidationError(f"Template not found: {t}"))

        if field_errors:
            raise ValidationError(field_errors)
        if template_errors:
            raise ValidationError(template_errors)

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

    @staticmethod
    def for_user(user: User):
        for group in user.groups.all():
            if hasattr(group, "transit_agency"):
                return group.transit_agency  # this is looking at the TransitAgency's staff_group

        # the loop above returns the first match found. Return None if no match was found.
        return None


class EnrollmentMethods:
    DIGITAL = "digital"
    IN_PERSON = "in_person"


SUPPORTED_METHODS = (
    (EnrollmentMethods.DIGITAL, EnrollmentMethods.DIGITAL.capitalize()),
    (EnrollmentMethods.IN_PERSON, EnrollmentMethods.IN_PERSON.replace("_", "-").capitalize()),
)


class EnrollmentFlow(models.Model):
    """Represents a user journey through the Benefits app for a single eligibility type."""

    id = models.AutoField(primary_key=True)
    system_name = models.SlugField(
        help_text="Primary internal system name for this EnrollmentFlow instance, e.g. in analytics and Eligibility API requests."  # noqa: 501
    )
    label = models.TextField(
        blank=True,
        default="",
        help_text="A human readable label, used as the display text in Admin.",
    )
    transit_agency = models.ForeignKey(TransitAgency, on_delete=models.PROTECT, null=True, blank=True)
    supported_enrollment_methods = MultiSelectField(
        choices=SUPPORTED_METHODS,
        max_choices=2,
        max_length=50,
        default=[EnrollmentMethods.DIGITAL, EnrollmentMethods.IN_PERSON],
        help_text="If the flow is supported by digital enrollment, in-person enrollment, or both",
    )
    group_id = models.TextField(
        blank=True, default="", help_text="Reference to the TransitProcessor group for user enrollment"
    )
    claims_provider = models.ForeignKey(
        ClaimsProvider,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="An entity that provides claims for eligibility verification for this flow.",
    )
    claims_scope = models.TextField(
        blank=True,
        default="",
        help_text="A space-separated list of identifiers used to specify what access privileges are being requested",
    )
    claims_eligibility_claim = models.TextField(
        blank=True, default="", help_text="The name of the claim that is used to verify eligibility"
    )
    claims_extra_claims = models.TextField(blank=True, default="", help_text="A space-separated list of any additional claims")
    claims_scheme_override = models.TextField(
        help_text="The authentication scheme to use (Optional). If blank, defaults to the value in Claims providers",
        default="",
        blank=True,
        verbose_name="Claims scheme",
    )
    eligibility_api_url = models.TextField(
        blank=True, default="", help_text="Fully qualified URL for an Eligibility API server used by this flow."
    )
    eligibility_api_auth_header = models.TextField(
        blank=True,
        default="",
        help_text="The auth header to send in Eligibility API requests for this flow.",
    )
    eligibility_api_auth_key_secret_name = SecretNameField(
        blank=True,
        default="",
        help_text="The name of a secret containing the value of the auth header to send in Eligibility API requests for this flow.",  # noqa: 501
    )
    eligibility_api_public_key = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The public key used to encrypt Eligibility API requests and to verify signed Eligibility API responses for this flow.",  # noqa: E501
    )
    eligibility_api_jwe_cek_enc = models.TextField(
        blank=True,
        default="",
        help_text="The JWE-compatible Content Encryption Key (CEK) key-length and mode to use in Eligibility API requests for this flow.",  # noqa: E501
    )
    eligibility_api_jwe_encryption_alg = models.TextField(
        blank=True,
        default="",
        help_text="The JWE-compatible encryption algorithm to use in Eligibility API requests for this flow.",
    )
    eligibility_api_jws_signing_alg = models.TextField(
        blank=True,
        default="",
        help_text="The JWS-compatible signing algorithm to use in Eligibility API requests for this flow.",
    )
    eligibility_form_class = models.TextField(
        blank=True,
        default="",
        help_text="The fully qualified Python path of a form class used by this flow, e.g. benefits.eligibility.forms.FormClass",  # noqa: E501
    )
    selection_label_template_override = models.TextField(
        blank=True,
        default="",
        help_text="Override the default template that defines the end-user UI for selecting this flow among other options.",
    )
    eligibility_start_template_override = models.TextField(
        blank=True,
        default="",
        help_text="Override the default template for the informational page of this flow.",
    )
    eligibility_unverified_template_override = models.TextField(
        blank=True,
        default="",
        help_text="Override the default template that defines the page when a user fails eligibility verification for this flow.",  # noqa: E501
    )
    help_template = models.TextField(
        blank=True,
        default="",
        help_text="Path to a Django template that defines the help text for this enrollment flow, used in building the dynamic help page for an agency",  # noqa: E501
    )
    supports_expiration = models.BooleanField(
        default=False, help_text="Indicates if the enrollment expires or does not expire"
    )
    expiration_days = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="If the enrollment supports expiration, number of days before the eligibility expires"
    )
    expiration_reenrollment_days = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="If the enrollment supports expiration, number of days preceding the expiration date during which a user can re-enroll in the eligibilty",  # noqa: E501
    )
    enrollment_index_template_override = models.TextField(
        blank=True,
        default="",
        help_text="Override the default template for the Eligibility Confirmation page (the index of the enrollment app)",
    )
    reenrollment_error_template = models.TextField(
        blank=True, default="", help_text="Template for a re-enrollment error associated with the enrollment flow"
    )
    enrollment_success_template_override = models.TextField(
        blank=True,
        default="",
        help_text="Override the default template for a successful enrollment associated with the enrollment flow",
    )
    display_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.label

    @property
    def agency_card_name(self):
        if self.uses_claims_verification:
            return ""
        else:
            return f"{self.transit_agency.slug}-agency-card"

    @property
    def eligibility_api_auth_key(self):
        if self.eligibility_api_auth_key_secret_name is not None:
            return get_secret_by_name(self.eligibility_api_auth_key_secret_name)
        else:
            return None

    @property
    def eligibility_api_public_key_data(self):
        """This flow's Eligibility API public key as a string."""
        return self.eligibility_api_public_key.data

    @property
    def selection_label_template(self):
        prefix = "eligibility/includes/selection-label"
        if self.uses_claims_verification:
            return self.selection_label_template_override or f"{prefix}--{self.system_name}.html"
        else:
            return self.selection_label_template_override or f"{prefix}--{self.agency_card_name}.html"

    @property
    def eligibility_start_template(self):
        prefix = "eligibility/start"
        if self.uses_claims_verification:
            return self.eligibility_start_template_override or f"{prefix}--{self.system_name}.html"
        else:
            return self.eligibility_start_template_override or f"{prefix}--{self.agency_card_name}.html"

    @property
    def eligibility_unverified_template(self):
        prefix = "eligibility/unverified"
        if self.uses_claims_verification:
            return self.eligibility_unverified_template_override or f"{prefix}.html"
        else:
            return self.eligibility_unverified_template_override or f"{prefix}--{self.agency_card_name}.html"

    @property
    def uses_claims_verification(self):
        """True if this flow verifies via the claims provider and has a scope and claim. False otherwise."""
        return self.claims_provider is not None and bool(self.claims_scope) and bool(self.claims_eligibility_claim)

    @property
    def claims_scheme(self):
        return self.claims_scheme_override or self.claims_provider.scheme

    @property
    def claims_all_claims(self):
        claims = [self.claims_eligibility_claim]
        if self.claims_extra_claims is not None:
            claims.extend(self.claims_extra_claims.split())
        return claims

    @property
    def eligibility_verifier(self):
        """A str representing the entity that verifies eligibility for this flow.

        Either the client name of the flow's claims provider, or the URL to the eligibility API.
        """
        if self.uses_claims_verification:
            return self.claims_provider.client_name
        else:
            return self.eligibility_api_url

    @property
    def enrollment_index_template(self):
        prefix = "enrollment/index"
        if self.uses_claims_verification:
            return self.enrollment_index_template_override or f"{prefix}.html"
        else:
            return self.enrollment_index_template_override or f"{prefix}--agency-card.html"

    @property
    def enrollment_success_template(self):
        prefix = "enrollment/success"
        if self.uses_claims_verification:
            return self.enrollment_success_template_override or f"{prefix}--{self.transit_agency.slug}.html"
        else:
            return self.enrollment_success_template_override or f"{prefix}--{self.agency_card_name}.html"

    def clean(self):
        field_errors = {}
        template_errors = []

        if self.supports_expiration:
            expiration_days = self.expiration_days
            expiration_reenrollment_days = self.expiration_reenrollment_days
            reenrollment_error_template = self.reenrollment_error_template

            message = "When support_expiration is True, this value must be greater than 0."
            if expiration_days is None or expiration_days <= 0:
                field_errors.update(expiration_days=ValidationError(message))
            if expiration_reenrollment_days is None or expiration_reenrollment_days <= 0:
                field_errors.update(expiration_reenrollment_days=ValidationError(message))
            if not reenrollment_error_template:
                field_errors.update(reenrollment_error_template=ValidationError("Required when supports expiration is True."))

        if self.transit_agency and self.transit_agency.active:
            self.transit_agency.clean()

            if self.claims_provider:
                message = "Required for claims verification."
                needed = dict(
                    claims_scope=self.claims_scope,
                    claims_eligibility_claim=self.claims_eligibility_claim,
                )
                field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})
            else:
                message = "Required for Eligibility API verification."
                needed = dict(
                    eligibility_api_auth_header=self.eligibility_api_auth_header,
                    eligibility_api_auth_key_secret_name=self.eligibility_api_auth_key_secret_name,
                    eligibility_api_jwe_cek_enc=self.eligibility_api_jwe_cek_enc,
                    eligibility_api_jwe_encryption_alg=self.eligibility_api_jwe_encryption_alg,
                    eligibility_api_jws_signing_alg=self.eligibility_api_jws_signing_alg,
                    eligibility_api_public_key=self.eligibility_api_public_key,
                    eligibility_api_url=self.eligibility_api_url,
                    eligibility_form_class=self.eligibility_form_class,
                )
                field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

            templates = [
                self.selection_label_template,
                self.eligibility_start_template,
                self.eligibility_unverified_template,
                self.enrollment_index_template,
                self.enrollment_success_template,
            ]
            if self.supports_expiration:
                templates.append(self.reenrollment_error_template)

            # since templates are calculated from the pattern or the override field
            # we can't add a field-level validation error
            # so just create directly for a missing template
            for t in templates:
                if not template_path(t):
                    template_errors.append(ValidationError(f"Template not found: {t}"))

        if field_errors:
            raise ValidationError(field_errors)
        if template_errors:
            raise ValidationError(template_errors)

    def eligibility_form_instance(self, *args, **kwargs):
        """Return an instance of this flow's EligibilityForm, or None."""
        if not bool(self.eligibility_form_class):
            return None

        # inspired by https://stackoverflow.com/a/30941292
        module_name, class_name = self.eligibility_form_class.rsplit(".", 1)
        FormClass = getattr(importlib.import_module(module_name), class_name)

        return FormClass(*args, **kwargs)

    @staticmethod
    def by_id(id):
        """Get an EnrollmentFlow instance by its ID."""
        logger.debug(f"Get {EnrollmentFlow.__name__} by id: {id}")
        return EnrollmentFlow.objects.get(id=id)


class EnrollmentEvent(models.Model):
    """A record of a successful enrollment."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    transit_agency = models.ForeignKey(TransitAgency, on_delete=models.PROTECT)
    enrollment_flow = models.ForeignKey(EnrollmentFlow, on_delete=models.PROTECT)
    enrollment_method = models.TextField(
        choices={
            EnrollmentMethods.DIGITAL: EnrollmentMethods.DIGITAL,
            EnrollmentMethods.IN_PERSON: EnrollmentMethods.IN_PERSON,
        }
    )
    verified_by = models.TextField()
    enrollment_datetime = models.DateTimeField(default=timezone.now)
    expiration_datetime = models.DateTimeField(blank=True, null=True)
    extra_claims = models.TextField(blank=True, default="")

    def __str__(self):
        dt = timezone.localtime(self.enrollment_datetime)
        ts = dt.strftime("%b %d, %Y, %I:%M %p")
        return f"{ts}, {self.transit_agency}, {self.enrollment_flow}"
