"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from . import api
from .forms import EligibilityVerificationForm
from eligibility_verification.core import models


def index(request):
    if request.method == "POST":
        form = EligibilityVerificationForm(request.POST)
        result = _verify(request, form)
    else:
        form = EligibilityVerificationForm(auto_id=True, label_suffix="")
        result = None

    return result or TemplateResponse(request, "eligibility/index.html", {"form": form})


def _verify(request, form):
    if not form.is_valid():
        return None

    agency = models.TransitAgency.get(request.session["agency"])
    sub, name = form.cleaned_data["card"], form.cleaned_data["last_name"]
    result = api.verify(sub, name, agency)

    if result:
        return HttpResponseRedirect(reverse("eligibility:verified"))
    else:
        return HttpResponseRedirect(reverse("eligibility:unverified"))


def verified(request):
    return TemplateResponse(request, "eligibility/verified.html")


def unverified(request):
    return TemplateResponse(request, "eligibility/unverified.html")
