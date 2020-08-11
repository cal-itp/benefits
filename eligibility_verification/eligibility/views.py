"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from . import api
from .forms import EligibilityVerificationForm


def index(request):
    if request.method == "POST":
        form = EligibilityVerificationForm(request.POST)
        if form.is_valid():
            result = api.verify(form.cleaned_data)
            if result:
                return HttpResponseRedirect(reverse("eligibility:verified"))
            else:
                return HttpResponseRedirect(reverse("eligibility:unverified"))
    else:
        form = EligibilityVerificationForm(auto_id=True, label_suffix="")

    return TemplateResponse(request, "eligibility/index.html", {"form": form})


def verified(request):
    return TemplateResponse(request, "eligibility/verified.html")


def unverified(request):
    return TemplateResponse(request, "eligibility/unverified.html")
