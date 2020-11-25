"""
The core application: view definition for the root of the webapp.
"""
from django.template.response import TemplateResponse
from django.urls import reverse

from . import models, viewmodels


def index(request):
    # reset the agency ref
    request.session["agency"] = None

    # query all active agencies
    agencies = models.TransitAgency.all_active()

    # generate a button to the landing page for each
    buttons = [
        viewmodels.Button(classes="btn-primary", text=a.long_name, url=reverse("core:agency_index", args=[a.slug]))
        for a in agencies
    ]

    # build the page vm
    page = viewmodels.Page(
        title="Transit Discount Eligibility Verification",
        icon=viewmodels.Icon("creditcardsuccess", "Credit card icon"),
        content_title="Get your Senior discount every time you use your credit card",
        paragraphs=[
            "We can verify your Senior status using your ID and make sure your discounted fare is always applied.",
            "It's easy! You'll need:"
        ],
        steps=[
            "Your California ID",
            "A credit card"
        ],
        buttons=buttons
    )

    context = page.context_dict()
    return TemplateResponse(request, "core/page.html", context)


def agency_index(request, agency):
    # keep a ref to the agency that initialized this session
    request.session["agency"] = agency.id

    # build the page vm
    page = viewmodels.Page(
        title="Transit Discount Eligibility Verification",
        icon=viewmodels.Icon("creditcardsuccess", "Credit card icon"),
        content_title=f"Get your Senior discount every time you use your credit card with {agency.long_name}",
        paragraphs=[
            "We can verify your Senior status using your ID and make sure your discounted fare is always applied.",
            "It's easy! You'll need:"
        ],
        steps=[
            "Your California ID",
            "A credit card"
        ],
        button=viewmodels.Button(
            classes="btn-primary",
            text="Let's do it!",
            url="eligibility:index"
        )
    )

    context = page.context_dict()
    return TemplateResponse(request, "core/page.html", context)
