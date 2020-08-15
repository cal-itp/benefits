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
        paragraphs=[],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix="")
    )
    context = viewmodels.page_context(page)

    if request.method == "POST":
        form = forms.EligibilityVerificationForm(request.POST)
        response = _verify(request, form)

        if response is None:
            page.form = form
            context = viewmodels.page_context(page)
            response = TemplateResponse(request, "core/page.html", context)
    else:
        response = TemplateResponse(request, "core/page.html", context)

    return response


def _verify(request, form):
    """"Helper calls the eligibility verification API to verify user input."""

    if not form.is_valid():
        return None

    sub, name = form.cleaned_data["card"], form.cleaned_data["last_name"]

    if not all((sub, name)):
        return error(request, {"error": "Missing data", "sub": sub, "name": name})

    agency = None
    if "agency" in request.session:
        agency = models.TransitAgency.get(request.session["agency"])

    try:
        types, results, errors = api.verify(sub, name, agency)
    except Exception:
        return error(request, {"error": "Problem communicating with API server"})

    if any(types):
        debug = {"eligibility": types, "results": results} if DEBUG else None
        return verified(request, types, debug)
    else:
        debug = {"errors": errors, "results": results} if DEBUG else None
        return unverified(request, errors, debug)


def verified(request, verified_types, debug=None):
    """View handler for the verified eligiblity page."""

    page = viewmodels.Page(
        title="Verified | Eligibility verification",
        content_title="Eligibility has been verified!",
        paragraphs=["Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore."],
        debug=debug
    )
    context = viewmodels.page_context(page)
    request.session["eligibility"] = verified_types
    return TemplateResponse(request, "core/page.html", context)


def unverified(request, errors, debug=None):
    """View handler for the unverified eligiblity page."""

    page = viewmodels.Page(
        title="Unverified | Eligibility verification",
        content_title="Eligibility could not be verified",
        paragraphs=["Sed do eiusmod tempor incididunt ut labore, consectetur adipiscing elit, lorem ipsum dolor sit amet."],
        debug=debug
    )
    context = viewmodels.page_context(page)
    return TemplateResponse(request, "core/page.html", context)


def error(request, errors={}):
    context = {"errors": errors}
    return TemplateResponse(request, "core/error.html", context)
