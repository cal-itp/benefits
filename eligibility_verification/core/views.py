"""
The core application: view definition for the root of the webapp.
"""
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
