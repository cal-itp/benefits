from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .forms import EligibilityVerificationForm


def index(request):
    form = EligibilityVerificationForm(auto_id=True, label_suffix="")
    return render(request, "eligibility/index.html", {"form": form})


def verify(request):
    form = EligibilityVerificationForm(request.POST)
    if form.is_valid():
        return HttpResponseRedirect(reverse("eligibility:verified"))
    else:
        return HttpResponseRedirect(reverse("eligibility:unverified"))


def verified(request):
    return render(request, "eligibility/verified.html")


def unverified(request):
    return render(request, "eligibility/unverified.html")
