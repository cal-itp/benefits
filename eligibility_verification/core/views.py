"""
The core application: view definition for the root of the webapp.
"""
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse

from . import models, session, viewmodels


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

    # build the page vm
    page = viewmodels.page_from_base(buttons=buttons)
    page.paragraphs.append("Choose your transit provider")

    return TemplateResponse(request, "core/page.html", page.context_dict())


def agency_index(request, agency):
    """View handler for an agency entry page."""

    session.update(request, agency=agency, origin=reverse("core:agency_index", args=[agency.slug]))

    # build the page vm
    page = viewmodels.page_from_base(
        button=viewmodels.Button.primary(
            text="Let’s do it!",
            url=reverse("eligibility:index")
        )
    )

    return TemplateResponse(request, "core/page.html", page.context_dict())


def _home_button(request):
    """Create a button pointing back to the correct landing page for the current session."""
    return viewmodels.Button(text="Return home", url=session.origin(request))


def bad_request(request, exception, template_name="400.html"):
    """View handler for HTTP 400 Bad Request responses."""
    home = _home_button(request)
    page = viewmodels.error_from_base(button=home)
    t = loader.get_template(template_name)
    return HttpResponseBadRequest(t.render(page.context_dict()))


def page_not_found(request, exception, template_name="404.html"):
    """View handler for HTTP 404 Not Found responses."""
    home = _home_button(request)
    page = viewmodels.not_found_from_base(button=home, path=request.path)
    t = loader.get_template(template_name)
    return HttpResponseNotFound(t.render(page.context_dict()))


def server_error(request, template_name="500.html"):
    """View handler for HTTP 500 Server Error responses."""
    home = _home_button(request)
    page = viewmodels.error_from_base(button=home)
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(page.context_dict()))
