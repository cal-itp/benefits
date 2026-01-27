import logging
import uuid

from cdt_identity.models import ClaimsVerificationRequest, IdentityGatewayConfig
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField

from benefits.core import context as core_context
from benefits.eligibility import context as eligibility_context
from benefits.enrollment import context as enrollment_context
from benefits.in_person import context as in_person_context

from .common import PemData, SecretNameField, template_path
from .transit import TransitAgency

logger = logging.getLogger(__name__)


class EnrollmentMethods:
    DIGITAL = "digital"
    IN_PERSON = "in_person"


SUPPORTED_METHODS = (
    (EnrollmentMethods.DIGITAL, EnrollmentMethods.DIGITAL.capitalize()),
    (EnrollmentMethods.IN_PERSON, EnrollmentMethods.IN_PERSON.replace("_", "-").capitalize()),
)


class EligibilityApiVerificationRequest(models.Model):
    """Represents configuration for eligibility verification via Eligibility API calls."""

    id = models.AutoField(primary_key=True)
    label = models.SlugField(
        help_text="A human readable label, used as the display text in Admin.",
    )
    api_url = models.URLField(help_text="Fully qualified URL for an Eligibility API server.")
    api_auth_header = models.CharField(
        help_text="The auth header to send in Eligibility API requests.",
        max_length=50,
    )
    api_auth_key_secret_name = SecretNameField(
        help_text="The name of a secret containing the value of the auth header to send in Eligibility API requests.",
    )
    client_private_key = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        default=None,
        null=True,
        help_text="Private key used to sign Eligibility API tokens created on behalf of the Benefits client.",
    )
    client_public_key = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        default=None,
        null=True,
        help_text="Public key corresponding to the Benefits client's private key, used by Eligibility Verification servers to encrypt responses.",  # noqa: E501
    )
    api_public_key = models.ForeignKey(
        PemData,
        related_name="+",
        on_delete=models.PROTECT,
        help_text="The public key used to encrypt Eligibility API requests and to verify signed Eligibility API responses.",
    )
    api_jwe_cek_enc = models.CharField(
        help_text="The JWE-compatible Content Encryption Key (CEK) key-length and mode to use in Eligibility API requests.",
        max_length=50,
    )
    api_jwe_encryption_alg = models.CharField(
        help_text="The JWE-compatible encryption algorithm to use in Eligibility API requests.",
        max_length=50,
    )
    api_jws_signing_alg = models.CharField(
        help_text="The JWS-compatible signing algorithm to use in Eligibility API requests.",
        max_length=50,
    )

    def __str__(self):
        return self.label

    @property
    def api_auth_key(self):
        """The Eligibility API auth key as a string."""
        secret_field = self._meta.get_field("api_auth_key_secret_name")
        return secret_field.secret_value(self)

    @property
    def client_private_key_data(self):
        """The private key used to sign Eligibility API tokens created by the Benefits client as a string."""
        return self.client_private_key.data

    @property
    def client_public_key_data(self):
        """The public key corresponding to the Benefits client's private key as a string."""
        return self.client_public_key.data

    @property
    def api_public_key_data(self):
        """The Eligibility API public key as a string."""
        return self.api_public_key.data


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
    sign_out_button_template = models.TextField(default="", blank=True, help_text="Template that renders sign-out button")
    sign_out_link_template = models.TextField(default="", blank=True, help_text="Template that renders sign-out link")
    oauth_config = models.ForeignKey(
        IdentityGatewayConfig,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The IdG connection details for this flow.",
    )
    claims_request = models.ForeignKey(
        ClaimsVerificationRequest,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The claims request details for this flow.",
    )
    api_request = models.ForeignKey(
        EligibilityApiVerificationRequest,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The Eligibility API request details for this flow.",
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
    display_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        agency_slug = self.transit_agency.slug if self.transit_agency else "no agency"
        return f"{self.label} ({agency_slug})"

    @property
    def group_id(self):
        if hasattr(self, "enrollmentgroup"):
            enrollment_group = self.enrollmentgroup

            # these are the class names for models in enrollment_littlepay and enrollment_switchio
            if hasattr(enrollment_group, "littlepaygroup"):
                return str(enrollment_group.littlepaygroup.group_id)
            elif hasattr(enrollment_group, "switchiogroup"):
                return enrollment_group.switchiogroup.group_id
            else:
                return None
        else:
            return None

    @property
    def agency_card_name(self):
        if self.uses_api_verification:
            return f"{self.transit_agency.slug}-agency-card"
        else:
            return ""

    @property
    def eligibility_api_auth_key(self):
        if self.uses_api_verification:
            return self.api_request.api_auth_key
        else:
            return None

    @property
    def eligibility_api_public_key_data(self):
        """This flow's Eligibility API public key as a string."""
        if self.uses_api_verification:
            return self.api_request.api_public_key_data
        else:
            return None

    @property
    def selection_label_template(self):
        prefix = "eligibility/includes/selection-label"
        if self.uses_api_verification:
            return f"{prefix}--{self.agency_card_name}.html"
        else:
            return f"{prefix}--{self.system_name}.html"

    @property
    def eligibility_start_context(self):
        return eligibility_context.eligibility_start[self.system_name].dict()

    @property
    def eligibility_unverified_context(self):
        ctx = eligibility_context.eligibility_unverified.get(self.system_name)
        return ctx.dict() if ctx else {}

    @property
    def uses_claims_verification(self):
        """True if this flow verifies via the Identity Gateway and has a scope and claim. False otherwise."""
        return (
            self.oauth_config is not None and bool(self.claims_request.scopes) and bool(self.claims_request.eligibility_claim)
        )

    @property
    def uses_api_verification(self):
        """True if this flow verifies via the Eligibility API. False otherwise."""
        return self.api_request is not None

    @property
    def claims_scheme(self):
        if self.uses_claims_verification:
            return self.claims_request.scheme or self.oauth_config.scheme
        else:
            return None

    @property
    def eligibility_verifier(self):
        """A str representing the entity that verifies eligibility for this flow.

        Either the client name of the flow's claims provider, or the URL to the eligibility API.
        """
        if self.uses_claims_verification:
            return self.oauth_config.client_name
        elif self.uses_api_verification:
            return self.api_request.api_url
        else:
            return "undefined"

    @property
    def enrollment_index_context(self):
        ctx = enrollment_context.enrollment_index.get(self.system_name, enrollment_context.DefaultEnrollmentIndex())
        return ctx.dict()

    @property
    def in_person_eligibility_context(self):
        return in_person_context.eligibility_index[self.system_name].dict()

    @property
    def help_context(self):
        ctx = core_context.flows_help.get(self.system_name)
        return [c.dict() for c in ctx] if ctx else []

    @property
    def supports_sign_out(self):
        return bool(self.sign_out_button_template) or bool(self.sign_out_link_template)

    def clean(self):
        errors = []

        if self.transit_agency:
            templates = [
                self.selection_label_template,
            ]

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

            if self.transit_agency.active and self.group_id is None:
                errors.append(
                    ValidationError(f"{self.system_name} needs either a LittlepayGroup or SwitchioGroup linked to it.")
                )

        if errors:
            raise ValidationError(errors)

    @staticmethod
    def by_id(id):
        """Get an EnrollmentFlow instance by its ID."""
        logger.debug(f"Get {EnrollmentFlow.__name__} by id: {id}")
        return EnrollmentFlow.objects.get(id=id)


class EnrollmentGroup(models.Model):
    id = models.AutoField(primary_key=True)
    enrollment_flow = models.OneToOneField(
        EnrollmentFlow,
        on_delete=models.PROTECT,
        help_text="The enrollment flow that this group is for.",
    )

    def __str__(self):
        return str(self.enrollment_flow)


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
