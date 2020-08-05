import random


from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def index(request):
    return render(request, "eligibility/index.html")


def verify(request):
    if random.choice([True, False]):
        return HttpResponseRedirect(reverse("eligibility:verified"))
    else:
        return HttpResponseRedirect(reverse("eligibility:unverified"))


def verified(request):
    return render(request, "eligibility/verified.html")


def unverified(request):
    return render(request, "eligibility/unverified.html")
