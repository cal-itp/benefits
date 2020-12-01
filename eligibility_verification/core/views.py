"""
The core application: view definition for the root of the webapp.
"""
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse

from . import models, session, viewmodels


def PageTemplateResponse(request, page_vm):
    """Helper returns a TemplateResponse using the common page template."""
    return TemplateResponse(request, "core/page.html", page_vm.context_dict())


def index(request):
    """View handler for the main entry page."""

    session.reset(request)

    # query all active agencies
    agencies = models.TransitAgency.all_active()

    # generate a button to the landing page for each
    buttons = [
        viewmodels.Button.outline_primary(
            text=a.long_name,
            url=reverse("core:agency_index", args=[a.slug])
        )
        for a in agencies
    ]
    buttons[0].classes.append("mt-3")
    buttons[0].label = "Choose your transit provider"

    # build the page vm
    page = viewmodels.Page.from_base(buttons=buttons)

    return PageTemplateResponse(request, page)


def agency_index(request, agency):
    """View handler for an agency entry page."""

    session.update(request, agency=agency, origin=reverse("core:agency_index", args=[agency.slug]))

    # build the page vm
    page = viewmodels.Page.from_base(
        button=viewmodels.Button.primary(
            text="Let’s do it!",
            url=reverse("eligibility:index")
        )
    )

    return PageTemplateResponse(request, page)


def bad_request(request, exception, template_name="400.html"):
    """View handler for HTTP 400 Bad Request responses."""
    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.error(button=home)
    t = loader.get_template(template_name)
    return HttpResponseBadRequest(t.render(page.context_dict()))


def page_not_found(request, exception, template_name="404.html"):
    """View handler for HTTP 404 Not Found responses."""
    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.not_found(button=home, path=request.path)
    t = loader.get_template(template_name)
    return HttpResponseNotFound(t.render(page.context_dict()))


def server_error(request, template_name="500.html"):
    """View handler for HTTP 500 Server Error responses."""
    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.error(button=home)
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(page.context_dict()))
