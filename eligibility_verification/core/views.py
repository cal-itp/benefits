"""
The core application: view definition for the root of the webapp.
"""
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse


def index(request):
    if request.session["agency"]:
        return TemplateResponse(request, "core/index.html")
    else:
        return HttpResponseRedirect(reverse("core:error"))


def error(request):
    return TemplateResponse(request, "core/error.html")
