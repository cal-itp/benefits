"""
The core application: view definition for the root of the webapp.
"""
from django.template.response import TemplateResponse

from . import viewmodels


def index(request):
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
        next_button=viewmodels.Button(
            classes="btn-primary",
            text="Let's do it!",
            url="eligibility:index"
        )
    )

    context = page.context_dict()
    return TemplateResponse(request, "core/page.html", context)


def error(request):
    return TemplateResponse(request, "core/error.html")
