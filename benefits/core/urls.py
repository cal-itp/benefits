"""
The core application: URLConf for the root of the webapp.
"""
import logging

from django.urls import path, register_converter
from django.urls.converters import StringConverter

from . import models, views


logger = logging.getLogger(__name__)


class TransitAgencyPathConverter:
    """Path converter to parse valid TransitAgency objects from URL paths."""

    # used to test the url fragment, determines if this PathConverter is used
    regex = "[a-zA-Z]{3,5}"

    def to_python(self, value):
        """Determine if the matched fragment corresponds to an active Agency."""
        value = str(value).lower()
        logger.debug(f"Matched fragment from path: {value}")

        agency = models.TransitAgency.by_slug(value)
        if agency and agency.active:
            logger.debug("Path fragment is an active agency")
            return agency
        else:
            logger.error("Path fragment is not an active agency")
            raise ValueError("value")

    def to_url(self, agency):
        """Convert the Agency back into a string for a URL."""
        try:
            return agency.slug
        except AttributeError:
            return str(agency)


logger.debug(f"Register path converter: {TransitAgencyPathConverter.__name__}")
register_converter(TransitAgencyPathConverter, "agency")


class CustomSlugConverter(StringConverter):
    regex = "(?!eligibility)[-a-zA-Z0-9_]*"


logger.debug(f"Register converter: {CustomSlugConverter.__name__}")
register_converter(CustomSlugConverter, "custom-slug")

app_name = "core"

urlpatterns = [
    path("help", views.help, name="help"),
    path("payment-options", views.payment_options, name="payment_options"),
    path("<custom-slug:slug>", views.PageView.as_view(), name="index"),
    # I would just remove this, but there are usages of `reverse("core:agency_index")`` that will break if I do.
    path("<agency:agency>", views.agency_index, name="agency_index"),
]
