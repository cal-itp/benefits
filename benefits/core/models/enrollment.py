import importlib
import logging
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField

from .common import PemData, SecretNameField, template_path
from .claims import ClaimsProvider
from .transit import TransitAgency
from benefits.core import context as core_context
from benefits.eligibility import context as eligibility_context
from benefits.in_person import context as in_person_context

logger = logging.getLogger(__name__)


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
        choices=core_context.SystemName,
        help_text="Primary internal system name for this EnrollmentFlow instance, e.g. in analytics and Eligibility API requests.",  # noqa: 501
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
        if self.uses_api_verification:
            return f"{self.transit_agency.slug}-agency-card"
        else:
            return ""

    @property
    def eligibility_api_auth_key(self):
        if self.eligibility_api_auth_key_secret_name is not None:
            secret_field = self._meta.get_field("eligibility_api_auth_key_secret_name")
            return secret_field.secret_value(self)
        else:
            return None

    @property
    def eligibility_api_public_key_data(self):
        """This flow's Eligibility API public key as a string."""
        return self.eligibility_api_public_key.data

    @property
    def selection_label_template(self):
        prefix = "eligibility/includes/selection-label"
        if self.uses_api_verification:
            return self.selection_label_template_override or f"{prefix}--{self.agency_card_name}.html"
        else:
            return self.selection_label_template_override or f"{prefix}--{self.system_name}.html"

    @property
    def eligibility_start_context(self):
        return eligibility_context.eligibility_start[self.system_name].dict()

    @property
    def eligibility_unverified_context(self):
        ctx = eligibility_context.eligibility_unverified.get(self.system_name)
        return ctx.dict() if ctx else {}

    @property
    def uses_claims_verification(self):
        """True if this flow verifies via the claims provider and has a scope and claim. False otherwise."""
        return self.claims_provider is not None and bool(self.claims_scope) and bool(self.claims_eligibility_claim)

    @property
    def uses_api_verification(self):
        """True if this flow verifies via the Eligibility API. False otherwise."""
        return bool(self.eligibility_api_url) and bool(self.eligibility_form_class)

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
        if self.uses_api_verification:
            return self.enrollment_index_template_override or f"{prefix}--agency-card.html"
        else:
            return self.enrollment_index_template_override or f"{prefix}.html"

    @property
    def enrollment_success_template(self):
        prefix = "enrollment/success"
        if self.uses_api_verification:
            return self.enrollment_success_template_override or f"{prefix}--{self.agency_card_name}.html"
        else:
            return self.enrollment_success_template_override or f"{prefix}--{self.transit_agency.slug}.html"

    @property
    def in_person_eligibility_context(self):
        return in_person_context.eligibility_index[self.system_name].dict()

    @property
    def help_context(self):
        ctx = core_context.flows_help.get(self.system_name)
        return [c.dict() for c in ctx] if ctx else []

    def clean(self):
        errors = []

        if self.transit_agency:
            templates = [
                self.selection_label_template,
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
                    errors.append(ValidationError(f"Template not found: {t}"))

            if EnrollmentMethods.IN_PERSON in self.supported_enrollment_methods:
                try:
                    in_person_eligibility_context = self.in_person_eligibility_context
                except KeyError:
                    in_person_eligibility_context = None

                if not in_person_eligibility_context:
                    errors.append(
                        ValidationError(f"{self.system_name} not configured for In-person. Please uncheck to continue.")
                    )

        if errors:
            raise ValidationError(errors)

    def eligibility_form_instance(self, *args, **kwargs):
        """Return an instance of this flow's EligibilityForm, or None."""
        if not self.uses_api_verification:
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
