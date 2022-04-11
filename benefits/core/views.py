"""
The core application: view definition for the root of the webapp.
"""
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from . import middleware, models, session, viewmodels


def PageTemplateResponse(request, page_vm):
    """Helper returns a TemplateResponse using the common page template."""
    return TemplateResponse(request, "core/page.html", page_vm.context_dict())


def _index_content_title():
    """Helper returns the content title for the common index page."""
    return _("core.pages.index.content_title")


def _index_paragraphs():
    """Helper returns the content paragraphs for the common index page."""
    return [_("core.pages.index.p[0]"), _("core.pages.index.p[1]"), _("core.pages.index.p[2]")]


def _index_url():
    """Helper computes the index url path."""
    return reverse("core:index")


@middleware.pageview_decorator
def index(request):
    """View handler for the main entry page."""
    session.reset(request)

    # generate a button to the landing page for each active agency
    agencies = models.TransitAgency.all_active()
    buttons = [viewmodels.Button.outline_primary(text=a.short_name, url=a.index_url) for a in agencies]
    buttons[0].classes.append("mt-3")
    buttons[0].label = _("core.pages.index.chooseprovider")

    page = viewmodels.Page(
        content_title=_index_content_title(),
        paragraphs=_index_paragraphs(),
        buttons=buttons,
        classes="home",
    )

    return PageTemplateResponse(request, page)


@middleware.pageview_decorator
def agency_index(request, agency):
    """View handler for an agency entry page."""
    session.reset(request)
    session.update(request, agency=agency, origin=agency.index_url)

    page = viewmodels.Page(
        content_title=_index_content_title(),
        paragraphs=_index_paragraphs(),
        button=viewmodels.Button.primary(text=_("core.pages.index.continue"), url=reverse("eligibility:index")),
        classes="home",
    )

    return PageTemplateResponse(request, page)


@middleware.pageview_decorator
def help(request):
    """View handler for the help page."""
    if session.active_agency(request):
        agency = session.agency(request)
        buttons = viewmodels.Button.agency_contact_links(agency)
    else:
        buttons = [btn for a in models.TransitAgency.all_active() for btn in viewmodels.Button.agency_contact_links(a)]

    buttons.append(viewmodels.Button.home(request, _("core.buttons.back")))

    page = viewmodels.Page(
        title=_("core.buttons.help"),
        content_title=_("core.buttons.help"),
        buttons=buttons,
        classes="text-lg-center",
        noimage=True,
    )

    return TemplateResponse(request, "core/help.html", page.context_dict())


@middleware.pageview_decorator
def bad_request(request, exception, template_name="400.html"):
    """View handler for HTTP 400 Bad Request responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=_index_url())

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.error(button=home)
    t = loader.get_template(template_name)

    return HttpResponseBadRequest(t.render(page.context_dict()))


@middleware.pageview_decorator
def csrf_failure(request, reason):
    """
    View handler for CSRF_FAILURE_VIEW with custom data.
    """
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=_index_url())

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.not_found(button=home, path=request.path)
    t = loader.get_template("400.html")

    return HttpResponseNotFound(t.render(page.context_dict()))


@middleware.pageview_decorator
def page_not_found(request, exception, template_name="404.html"):
    """View handler for HTTP 404 Not Found responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=_index_url())

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.not_found(button=home, path=request.path)
    t = loader.get_template(template_name)

    return HttpResponseNotFound(t.render(page.context_dict()))


@middleware.pageview_decorator
def server_error(request, template_name="500.html"):
    """View handler for HTTP 500 Server Error responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=_index_url())

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.error(button=home)
    t = loader.get_template(template_name)

    return HttpResponseServerError(t.render(page.context_dict()))
