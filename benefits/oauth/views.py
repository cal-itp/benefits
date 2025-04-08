import logging
from django.template.response import TemplateResponse
from django.utils.decorators import decorator_from_middleware

from benefits.core import session
from benefits.core.middleware import AgencySessionRequired


logger = logging.getLogger(__name__)

TEMPLATE_SYSTEM_ERROR = "oauth/system_error.html"


@decorator_from_middleware(AgencySessionRequired)
def system_error(request):
    """View handler for an oauth system error."""

    # overwrite origin so that CTA takes user to agency index
    agency = session.agency(request)
    session.update(request, origin=agency.index_url)

    return TemplateResponse(request, TEMPLATE_SYSTEM_ERROR)
