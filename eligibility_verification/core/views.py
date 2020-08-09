"""
The core application: view definition for the root of the webapp.
"""
from django.template.response import TemplateResponse


def index(request):
    if request.session["agency"]:
        return TemplateResponse(request, "core/index.html")
    else:
        return TemplateResponse(request, "core/error.html")
