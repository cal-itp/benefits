"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from .forms import EligibilityVerificationForm


def _render_index(request, form=None):
    form = form or EligibilityVerificationForm(auto_id=True, label_suffix="")
    return TemplateResponse(request, "eligibility/index.html", {"form": form})


def index(request):
    return _render_index(request)


def verify(request):
    form = EligibilityVerificationForm(request.POST)
    if form.is_valid():
        return HttpResponseRedirect(reverse("eligibility:verified"))
    else:
        return _render_index(request, form)


def verified(request):
    return TemplateResponse(request, "eligibility/verified.html")


def unverified(request):
    return TemplateResponse(request, "eligibility/unverified.html")
