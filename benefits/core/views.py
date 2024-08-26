"""
The core application: view definition for the root of the webapp.
"""

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import redirect
from django.template import loader
from django.template.response import TemplateResponse

from benefits.routes import routes
from . import models, session
from .middleware import pageview_decorator, index_or_agencyindex_origin_decorator, user_error

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
def agency_index(request, agency: models.TransitAgency):
    """View handler for an agency entry page."""
    session.reset(request)
    session.update(request, agency=agency, origin=agency.index_url)

    return TemplateResponse(request, agency.index_template)


@pageview_decorator
def agency_eligibility_index(request, agency: models.TransitAgency):
    """View handler forwards the request to the agency's Eligibility Index (e.g. flow selection) page."""
    session.reset(request)
    session.update(request, agency=agency, origin=agency.index_url)

    return redirect(routes.ELIGIBILITY_INDEX)


@pageview_decorator
def agency_public_key(request, agency: models.TransitAgency):
    """View handler returns an agency's public key as plain text."""
    return HttpResponse(agency.eligibility_api_public_key_data, content_type="text/plain")


@pageview_decorator
def agency_card(request, agency: models.TransitAgency):
    """View handler forwards the request to the agency's Agency Card (e.g. Eligibility API) flow, or returns a user error."""
    session.reset(request)
    session.update(request, agency=agency, origin=agency.index_url)

    eligibility_api_flow = (
        agency.enrollment_flows.filter(eligibility_api_url__isnull=False, eligibility_form_class__isnull=False)
        .order_by("id")
        .last()
    )

    if eligibility_api_flow:
        session.update(request, flow=eligibility_api_flow)
        return redirect(routes.ELIGIBILITY_CONFIRM)
    else:
        return user_error(request)


@pageview_decorator
def help(request):
    """View handler for the help page."""
    return TemplateResponse(request, TEMPLATE_HELP)


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
    return TemplateResponse(request, TEMPLATE_LOGGED_OUT)
