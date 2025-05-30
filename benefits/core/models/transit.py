import os
import logging

from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.contrib.auth.models import Group, User
from django.db import models
from django.urls import reverse

from benefits.core import context as core_context
from benefits.eligibility import context as eligibility_context
from benefits.routes import routes
from .common import PemData

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
    portal_url = models.TextField(
        default="",
        blank=True,
        help_text="The absolute base URL for the TransitProcessor's control portal, including https://.",
    )

    def __str__(self):
        return self.name


class TransitAgency(models.Model):
    """An agency offering transit service."""

    class Meta:
        verbose_name_plural = "transit agencies"

    id = models.AutoField(primary_key=True)
    active = models.BooleanField(default=False, help_text="Determines if this Agency is enabled for users")
    slug = models.SlugField(
        choices=core_context.AgencySlug,
        help_text="Used for URL navigation for this agency, e.g. the agency homepage url is /{slug}",
    )
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
    littlepay_config = models.OneToOneField(
        "enrollment_littlepay.LittlepayConfig",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        help_text="The Littlepay configuration used by this agency for enrollment.",
    )
    switchio_config = models.ForeignKey(
        "enrollment_switchio.SwitchioConfig",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        help_text="The Switchio configuration used by this agency for enrollment.",
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
    def index_context(self):
        return core_context.agency_index[self.slug].dict()

    @property
    def index_url(self):
        """Public-facing URL to the TransitAgency's landing page."""
        return reverse(routes.AGENCY_INDEX, args=[self.slug])

    @property
    def eligibility_index_context(self):
        return eligibility_context.eligibility_index[self.slug].dict()

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
    def enrollment_flows(self):
        return self.enrollmentflow_set

    def clean(self):
        field_errors = {}
        non_field_errors = []

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
            field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

            if self.transit_processor:
                if self.littlepay_config is None and self.switchio_config is None:
                    non_field_errors.append(ValidationError("Must fill out configuration for either Littlepay or Switchio."))

            if self.littlepay_config:
                try:
                    self.littlepay_config.clean()
                except ValidationError as e:
                    message = "Littlepay configuration is missing fields that are required when this agency is active."
                    message += f" Missing fields: {', '.join(e.error_dict.keys())}"
                    non_field_errors.append(ValidationError(message))

            if self.switchio_config:
                try:
                    self.switchio_config.clean(agency=self)
                except ValidationError as e:
                    message = "Switchio configuration is missing fields that are required when this agency is active."
                    message += f" Missing fields: {', '.join(e.error_dict.keys())}"
                    non_field_errors.append(ValidationError(message))

        all_errors = {}
        if field_errors:
            all_errors.update(field_errors)
        if non_field_errors:
            all_errors.update({NON_FIELD_ERRORS: value for value in non_field_errors})
        if all_errors:
            raise ValidationError(all_errors)

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
