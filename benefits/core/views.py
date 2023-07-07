"""
The core application: view definition for the root of the webapp.
"""
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import pgettext, gettext as _

from . import models, session, viewmodels
from .middleware import pageview_decorator

ROUTE_INDEX = "core:index"
ROUTE_ELIGIBILITY = "eligibility:index"
ROUTE_HELP = "core:help"
ROUTE_LOGGED_OUT = "core:logged_out"

TEMPLATE_INDEX = "core/index.html"
TEMPLATE_AGENCY = "core/agency_index.html"
TEMPLATE_HELP = "core/help.html"
TEMPLATE_LOGGED_OUT = "core/logged_out.html"


@pageview_decorator
def index(request):
    """View handler for the main entry page."""
    session.reset(request)

    page = viewmodels.Page(
        title=_("core.pages.index.title"),
        headline=_("core.pages.index.headline"),
    )

    ctx = page.context_dict()
    ctx["agencies"] = [viewmodels.TransitAgency(a) for a in models.TransitAgency.all_active()]

    return TemplateResponse(request, TEMPLATE_INDEX, ctx)


@pageview_decorator
def agency_index(request, agency):
    """View handler for an agency entry page."""
    session.reset(request)
    session.update(request, agency=agency, origin=agency.index_url)

    button = viewmodels.Button.primary(text=_("core.pages.index.continue"), url=reverse(ROUTE_ELIGIBILITY))

    page = viewmodels.Page(
        title=_("core.pages.agency_index.title"),
        headline=_("core.pages.agency_index.headline%(transit_agency_short_name)s")
        % {"transit_agency_short_name": agency.short_name},
        button=button,
    )

    return TemplateResponse(request, TEMPLATE_AGENCY, page.context_dict())


@pageview_decorator
def agency_public_key(request, agency):
    """View handler returns an agency's public key as plain text."""
    return HttpResponse(agency.public_key_data, content_type="text/plain")


@pageview_decorator
def help(request):
    """View handler for the help page."""
    if session.active_agency(request):
        agency = session.agency(request)
        agency_links = viewmodels.Button.agency_contact_links(agency)
    else:
        agency_links = [btn for a in models.TransitAgency.all_active() for btn in viewmodels.Button.agency_contact_links(a)]

    back_button = viewmodels.Button.home(request, _("core.buttons.back"))

    page = viewmodels.Page(
        title=_("core.buttons.help"),
        headline=_("core.buttons.help"),
    )

    ctx = page.context_dict()
    ctx["agency_links"] = agency_links
    ctx["back_button"] = back_button

    return TemplateResponse(request, TEMPLATE_HELP, ctx)


@pageview_decorator
def bad_request(request, exception, template_name="400.html"):
    """View handler for HTTP 400 Bad Request responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=reverse(ROUTE_INDEX))

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.server_error(button=home)
    t = loader.get_template(template_name)

    return HttpResponseBadRequest(t.render(page.context_dict()))


@pageview_decorator
def csrf_failure(request, reason):
    """
    View handler for CSRF_FAILURE_VIEW with custom data.
    """
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=reverse(ROUTE_INDEX))

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.not_found(button=home, path=request.path)
    t = loader.get_template("400.html")

    return HttpResponseNotFound(t.render(page.context_dict()))


@pageview_decorator
def page_not_found(request, exception, template_name="404.html"):
    """View handler for HTTP 404 Not Found responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=reverse(ROUTE_INDEX))

    home = viewmodels.Button.home(request)
    # show a more user-friendly message instead of not_found
    page = viewmodels.ErrorPage.user_error(button=home, path=request.path)
    t = loader.get_template(template_name)

    return HttpResponseNotFound(t.render(page.context_dict()))


@pageview_decorator
def server_error(request, template_name="500.html"):
    """View handler for HTTP 500 Server Error responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=reverse(ROUTE_INDEX))

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.server_error(button=home)
    t = loader.get_template(template_name)

    return HttpResponseServerError(t.render(page.context_dict()))


def logged_out(request):
    """View handler for the final log out confirmation message."""
    page = viewmodels.Page(
        title=_("core.pages.logged_out.title"),
        icon=viewmodels.Icon("happybus", pgettext("image alt text", "core.icons.happybus")),
    )

    return TemplateResponse(request, TEMPLATE_LOGGED_OUT, page.context_dict())
