import logging
import os

from django.contrib.auth.models import Group, User
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.urls import reverse
from multiselectfield import MultiSelectField

from benefits.routes import routes

from .common import Environment

logger = logging.getLogger(__name__)


class CardSchemes:
    VISA = "visa"
    MASTERCARD = "mastercard"
    DISCOVER = "discover"
    AMEX = "amex"

    CHOICES = dict(
        [
            (VISA, "Visa"),
            (MASTERCARD, "Mastercard"),
            (DISCOVER, "Discover"),
            (AMEX, "American Express"),
        ]
    )


def agency_logo(instance, filename):
    base, ext = os.path.splitext(filename)
    return f"agencies/{instance.slug}" + ext


class TransitProcessorConfig(models.Model):
    id = models.AutoField(primary_key=True)
    environment = models.TextField(
        choices=Environment,
        help_text="A label to indicate which environment this configuration is for.",
    )
    transit_agency = models.OneToOneField(
        "TransitAgency",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        help_text="The transit agency that uses this configuration.",
    )
    portal_url = models.TextField(
        default="",
        blank=True,
        help_text="The absolute base URL for the TransitProcessor's control portal, including https://.",
    )

    def __str__(self):
        environment_label = Environment(self.environment).label if self.environment else "unknown"
        agency_slug = self.transit_agency.slug if self.transit_agency else "(no agency)"
        return f"({environment_label}) {agency_slug}"


class TransitAgency(models.Model):
    """An agency offering transit service."""

    class Meta:
        verbose_name_plural = "transit agencies"

    id = models.AutoField(primary_key=True)
    active = models.BooleanField(default=False, help_text="Determines if this Agency is enabled for users")
    slug = models.SlugField(
        unique=True,
        help_text="Used for URL navigation for this agency, e.g. the agency homepage url is /{slug}",
    )
    short_name = models.TextField(
        default="", help_text="The user-facing short name for this agency. Often an uppercase acronym."
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
    supported_card_schemes = MultiSelectField(
        choices=CardSchemes.CHOICES,
        min_choices=1,
        max_choices=len(CardSchemes.CHOICES),
        default=[CardSchemes.VISA, CardSchemes.MASTERCARD],
        help_text="The contactless card schemes this agency supports.",
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
        related_name="transit_agency",
    )
    logo = models.ImageField(
        default="",
        blank=True,
        upload_to=agency_logo,
        help_text="The transit agency's logo.",
    )

    def __str__(self):
        return self.long_name

    @property
    def index_url(self):
        """Public-facing URL to the TransitAgency's landing page."""
        return reverse(routes.AGENCY_INDEX, args=[self.slug])

    @property
    def eligibility_index_url(self):
        """Public facing URL to the TransitAgency's eligibility page."""
        return reverse(routes.AGENCY_ELIGIBILITY_INDEX, args=[self.slug])

    @property
    def littlepay_config(self):
        if hasattr(self, "transitprocessorconfig") and hasattr(self.transitprocessorconfig, "littlepayconfig"):
            return self.transitprocessorconfig.littlepayconfig
        else:
            return None

    @property
    def switchio_config(self):
        if hasattr(self, "transitprocessorconfig") and hasattr(self.transitprocessorconfig, "switchioconfig"):
            return self.transitprocessorconfig.switchioconfig
        else:
            return None

    @property
    def transit_processor(self):
        if self.littlepay_config:
            return "littlepay"
        elif self.switchio_config:
            return "switchio"
        else:
            return None

    @property
    def in_person_enrollment_index_route(self):
        """This Agency's in-person enrollment index route, based on its configured transit processor."""
        if self.littlepay_config:
            return routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX
        elif self.switchio_config:
            return routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX
        else:
            raise ValueError(
                (
                    "TransitAgency must have either a LittlepayConfig or SwitchioConfig "
                    "in order to show in-person enrollment index."
                )
            )

    @property
    def enrollment_index_route(self):
        """This Agency's enrollment index route, based on its configured transit processor."""
        if self.littlepay_config:
            return routes.ENROLLMENT_LITTLEPAY_INDEX
        elif self.switchio_config:
            return routes.ENROLLMENT_SWITCHIO_INDEX
        else:
            raise ValueError(
                "TransitAgency must have either a LittlepayConfig or SwitchioConfig in order to show enrollment index."
            )

    @property
    def enrollment_flows(self):
        return self.enrollmentflow_set

    @property
    def customer_service_group_name(self):
        """Returns the standardized name for this Agency's customer service group."""
        return f"{self.short_name} Customer Service"

    def clean(self):
        field_errors = {}
        non_field_errors = []

        if self.active:
            message = "This field is required for active transit agencies."
            needed = dict(
                long_name=self.long_name,
                phone=self.phone,
                info_url=self.info_url,
                logo=self.logo,
            )
            field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

            if self.littlepay_config is None and self.switchio_config is None:
                non_field_errors.append(ValidationError("Must fill out configuration for either Littlepay or Switchio."))
            else:
                if self.littlepay_config:
                    try:
                        self.littlepay_config.clean()
                    except ValidationError as e:
                        message = "Littlepay configuration is missing fields that are required when this agency is active."
                        message += f" Missing fields: {', '.join(e.error_dict.keys())}"
                        non_field_errors.append(ValidationError(message))

                if self.switchio_config:
                    try:
                        self.switchio_config.clean()
                    except ValidationError as e:
                        message = "Switchio configuration is missing fields that are required when this agency is active."
                        message += f" Missing fields: {', '.join(e.error_dict.keys())}"
                        non_field_errors.append(ValidationError(message))

        if self.pk:  # prohibit updating short_name with blank customer_service_group
            original_obj = TransitAgency.objects.get(pk=self.pk)
            if self.short_name != original_obj.short_name and not self.customer_service_group:
                field_errors.update(
                    {
                        "customer_service_group": ValidationError(
                            "Blank not allowed. Set to its original value if changing the Short Name."
                        )
                    }
                )

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
        return TransitAgency.objects.filter(active=True).order_by("long_name")

    @staticmethod
    def for_user(user: User):
        for group in user.groups.all():
            if hasattr(group, "transit_agency"):
                return group.transit_agency  # this is looking at the TransitAgency's customer_service_group

        # the loop above returns the first match found. Return None if no match was found.
        return None
