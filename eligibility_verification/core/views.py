"""
The core application: view definition for the root of the webapp.
"""
from django.template.response import TemplateResponse
from django.urls import reverse

from . import models, viewmodels


def index(request):
    """View handler for the main entry page."""

    # reset the agency ref
    request.session["agency"] = None

    # query all active agencies
    agencies = models.TransitAgency.all_active()

    # generate a button to the landing page for each
    buttons = [
        viewmodels.Button(
            classes="btn-outline-primary",
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

    # keep a ref to the agency that initialized this session
    request.session["agency"] = agency.id

    # build the page vm
    page = viewmodels.page_from_base(
        button=viewmodels.Button(
            classes="btn-primary",
            text="Let’s do it!",
            url=reverse("eligibility:index")
        )
    )

    return TemplateResponse(request, "core/page.html", page.context_dict())
