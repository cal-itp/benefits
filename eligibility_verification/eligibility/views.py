"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.template.response import TemplateResponse

from eligibility_verification.core import models
from . import api, forms


def index(request):
    """View handler for the eligibility verification form."""

    if request.method == "POST":
        form = forms.EligibilityVerificationForm(request.POST)
        result = _verify(request, form)
    else:
        form = forms.EligibilityVerificationForm(auto_id=True, label_suffix="")
        result = None

    return result or TemplateResponse(request, "eligibility/index.html", {"form": form})


def _verify(request, form):
    """"Helper calls the eligibility verification API to verify user input."""

    if not form.is_valid():
        return None

    agency = models.TransitAgency.get(request.session["agency"])
    sub, name = form.cleaned_data["card"], form.cleaned_data["last_name"]

    if not all((agency, sub, name)):
        return TemplateResponse(request, "core/error.html")

    results, errors = api.verify(agency, sub, name)

    if len(results) > 0:
        return verified(request, results)
    else:
        return unverified(request, errors)


def verified(request, results):
    return TemplateResponse(request, "eligibility/verified.html", {"results": results})


def unverified(request, errors):
    return TemplateResponse(request, "eligibility/unverified.html", {"errors": errors})
