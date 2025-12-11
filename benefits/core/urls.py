"""
The core application: URLConf for the root of the webapp.
"""

import logging

from django.urls import path, register_converter

from benefits.routes import routes
from . import models, views


logger = logging.getLogger(__name__)


class TransitAgencyPathConverter:
    """Path converter to parse valid TransitAgency objects from URL paths."""

    # used to test the url fragment, determines if this PathConverter is used
    regex = "[a-zA-Z]{3,}"

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

app_name = "core"

urlpatterns = [
    path("", views.IndexView.as_view(), name=routes.name(routes.INDEX)),
    path("help", views.HelpView.as_view(), name=routes.name(routes.HELP)),
    path("logged_out", views.logged_out, name=routes.name(routes.LOGGED_OUT)),
    path("error", views.server_error, name=routes.name(routes.SERVER_ERROR)),
    path("<agency:agency>", views.AgencyIndexView.as_view(), name=routes.name(routes.AGENCY_INDEX)),
    path("<agency:agency>/agency-card", views.agency_card, name=routes.name(routes.AGENCY_CARD)),
    path(
        "<agency:agency>/eligibility",
        views.AgencyEligibilityIndexView.as_view(),
        name=routes.name(routes.AGENCY_ELIGIBILITY_INDEX),
    ),
    path("<agency:agency>/publickey", views.AgencyPublicKeyView.as_view(), name=routes.name(routes.AGENCY_PUBLIC_KEY)),
]
