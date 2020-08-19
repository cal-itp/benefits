"""
The core application: view definition for the root of the webapp.
"""
from django.template.response import TemplateResponse

from . import viewmodels


def index(request):
    page = viewmodels.Page(
        title="Transit Discount Eligibility Verification",
        icon="creditcardsuccess",
        content_title="Let's see if you're eligible for a Senior discounted-fare",
        paragraphs=[
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        ],
        next_button=viewmodels.Button(
            classes="btn-primary",
            text="Get Started",
            url="eligibility:index"
        )
    )

    context = viewmodels.page_context(page)
    return TemplateResponse(request, "core/page.html", context)


def error(request):
    return TemplateResponse(request, "core/error.html")
