"""
The core application: view definition for the root of the webapp.
"""
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from . import session, viewmodels
from .middleware import pageview_decorator, index_or_agencyindex_origin_decorator

ROUTE_ELIGIBILITY = "eligibility:index"
ROUTE_HELP = "core:help"
ROUTE_LOGGED_OUT = "core:logged_out"

TEMPLATE_INDEX = "core/index.html"
TEMPLATE_AGENCY = "core/agency-index.html"
TEMPLATE_HELP = "core/help.html"
TEMPLATE_LOGGED_OUT = "core/logged-out.html"

TEMPLATE_BAD_REQUEST = "400.html"
TEMPLATE_NOT_FOUND = "404.html"
TEMPLATE_SERVER_ERROR = "500.html"


@pageview_decorator
def index(request):
    """View handler for the main entry page."""
    session.reset(request)

    return TemplateResponse(request, TEMPLATE_INDEX)


@pageview_decorator
def agency_index(request, agency):
    """View handler for an agency entry page."""
    session.reset(request)
    session.update(request, agency=agency, origin=agency.index_url)

    page = viewmodels.Page(
        title=_("core.pages.agency_index.title"),
        headline=_("core.pages.agency_index.headline%(transit_agency_short_name_and_type)s")
        % {"transit_agency_short_name_and_type": " ".join([agency.short_name, _(agency.transit_type)])},
    )

    return TemplateResponse(request, TEMPLATE_AGENCY, page.context_dict())


@pageview_decorator
def agency_public_key(request, agency):
    """View handler returns an agency's public key as plain text."""
    return HttpResponse(agency.public_key_data, content_type="text/plain")


@pageview_decorator
def help(request):
    """View handler for the help page."""
    page = viewmodels.Page(
        title=_("core.buttons.help"),
        headline=_("core.buttons.help"),
    )

    ctx = page.context_dict()
    return TemplateResponse(request, TEMPLATE_HELP, ctx)


@pageview_decorator
@index_or_agencyindex_origin_decorator
def bad_request(request, exception, template_name=TEMPLATE_BAD_REQUEST):
    """View handler for HTTP 400 Bad Request responses."""
    t = loader.get_template(template_name)

    return HttpResponseBadRequest(t.render(request=request))


@pageview_decorator
@index_or_agencyindex_origin_decorator
def csrf_failure(request, reason):
    """
    View handler for CSRF_FAILURE_VIEW with custom data.
    """
    t = loader.get_template(TEMPLATE_BAD_REQUEST)

    return HttpResponseNotFound(t.render(request=request))


@pageview_decorator
@index_or_agencyindex_origin_decorator
def page_not_found(request, exception, template_name=TEMPLATE_NOT_FOUND):
    """View handler for HTTP 404 Not Found responses."""
    t = loader.get_template(template_name)

    return HttpResponseNotFound(t.render(request=request))


@pageview_decorator
@index_or_agencyindex_origin_decorator
def server_error(request, template_name=TEMPLATE_SERVER_ERROR):
    """View handler for HTTP 500 Server Error responses."""
    t = loader.get_template(template_name)

    return HttpResponseServerError(t.render(request=request))


def logged_out(request):
    """View handler for the final log out confirmation message."""
    page = viewmodels.Page(title=_("core.pages.logged_out.title"))
    return TemplateResponse(request, TEMPLATE_LOGGED_OUT, page.context_dict())
