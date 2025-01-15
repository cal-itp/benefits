import os
import logging

from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, User
from django.db import models
from django.urls import reverse

from benefits.routes import routes
from .common import PemData, SecretNameField, template_path

logger = logging.getLogger(__name__)


def _agency_logo(instance, filename, size):
    base, ext = os.path.splitext(filename)
    return f"agencies/{instance.slug}-{size}" + ext


def agency_logo_small(instance, filename):
    return _agency_logo(instance, filename, "sm")


def agency_logo_large(instance, filename):
    return _agency_logo(instance, filename, "lg")


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
        secret_field = self._meta.get_field("transit_processor_client_secret_name")
        return secret_field.secret_value(self)

    @property
    def enrollment_flows(self):
        return self.enrollmentflow_set

    def clean(self):
        field_errors = {}
        template_errors = []

        if self.active:
            for flow in self.enrollment_flows.all():
                try:
                    flow.clean()
                except ValidationError:
                    raise ValidationError(f"Invalid EnrollmentFlow: {flow.label}")

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
