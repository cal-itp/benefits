"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.template.response import TemplateResponse

from eligibility_verification.core import models, viewmodels
from eligibility_verification.settings import DEBUG
from . import api, forms


def index(request):
    """View handler for the eligibility verification form."""

    page = viewmodels.Page(
        title="Eligibility verification",
        content_title="Let's see if we can pull your Senior status from the DMV",
        paragraphs=[
            "We use this to check which programs you could participate in."
        ],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix="")
    )
    context = page.context_dict()

    if request.method == "POST":
        form = forms.EligibilityVerificationForm(request.POST)
        response = _verify(request, form)

        if response is None:
            page.form = form
            context = page.context_dict()
            response = TemplateResponse(request, "core/page.html", context)
    else:
        response = TemplateResponse(request, "core/page.html", context)

    return response


def _verify(request, form):
    """"Helper calls the eligibility verification API to verify user input."""

    if not form.is_valid():
        return None

    sub, name = form.cleaned_data.get("card"), form.cleaned_data.get("last_name")

    if not all((sub, name)):
        return internal_error(request, sub is None, name is None)

    agency = None
    if "agency" in request.session:
        agency = models.TransitAgency.get(request.session["agency"])

    try:
        types, results, errors = api.verify(sub, name, agency)
    except Exception as ex:
        return server_error(request, {"exception": ex})

    if any(types):
        debug = {"eligibility": types, "results": results} if DEBUG else None
        return verified(request, types, debug)
    else:
        debug = {"errors": errors, "results": results} if DEBUG else None
        return unverified(request, errors, debug)


def verified(request, verified_types, debug=None):
    """View handler for the verified eligibility page."""

    page = viewmodels.Page(
        title="Verified | Eligibility verification",
        content_title="Great! Looks like you are eligible for a Senior discount",
        paragraphs=[
            "Next we need to match a credit card to the information you provided to verify it's really you."
        ],
        steps=[
            "Link your credit card. No charges will be made. Just identity verification.",
            "We make sure all relevant discounts are applied every time you use your credit card."
        ],
        next_button=viewmodels.Button(
            classes="btn-primary",
            text="Continue",
            url="#payments"
        ),
        debug=debug
    )
    context = page.context_dict()
    request.session["eligibility"] = verified_types
    return TemplateResponse(request, "core/page.html", context)


def unverified(request, errors, debug=None):
    """View handler for the unverified eligibility page."""

    page = viewmodels.Page(
        title="Unverified | Eligibility verification",
        content_title="Eligibility could not be verified",
        paragraphs=["Sed do eiusmod tempor incididunt ut labore, consectetur adipiscing elit, lorem ipsum dolor sit amet."],
        debug=debug
    )
    context = page.context_dict()
    return TemplateResponse(request, "core/page.html", context)


def internal_error(request, sub_missing, name_missing):
    page = viewmodels.ErrorPage(
        content_title="Our system is down",
        paragraphs=[
            "Unfortunately, our system is experiencing problems right now.",
            "Please check back later."
        ],
        button=viewmodels.Button(
            classes="btn-primary",
            text="Start over",
            url=""
        ),
        debug={"sub_missing": sub_missing, "name_missing": name_missing}
    )
    context = page.context_dict()
    return TemplateResponse(request, "core/page.html", context)


def server_error(request, debug={}):
    page = viewmodels.ErrorPage(
        content_title="Service is down",
        paragraphs=[
            "Unfortunately, we can't reach the verification service right now.",
            "Please check back later."
        ],
        button=viewmodels.Button(
            classes="btn-primary",
            text="Start over",
            url=""
        ),
        debug=debug
    )
    context = page.context_dict()
    return TemplateResponse(request, "core/page.html", context)
