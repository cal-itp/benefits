"""
The core application: URLConf for the root of the webapp.
"""
from django.urls import path, register_converter

from . import models, views


class TransitAgencyPathConverter():
    """Path converter to parse valid TransitAgency objects from URL paths."""

    # used to test the url fragment, determines if this PathConverter is used
    regex = "[a-zA-Z]{3,5}"

    def to_python(self, value):
        """Determine if the matched fragment corresponds to an active Agency."""
        value = str(value).lower()
        agency = models.TransitAgency.by_slug(value)
        if agency and agency.active:
            return agency
        else:
            raise ValueError()

    def to_url(self, agency):
        """Convert the Agency back into a string for a URL."""
        try:
            return agency.slug
        except AttributeError:
            return str(agency)


register_converter(TransitAgencyPathConverter, "agency")

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("<agency:agency>", views.agency_index, name="agency_index"),
    path("help", views.help, name="help"),
    path("payment-options", views.payment_options, name="payment_options"),
]
