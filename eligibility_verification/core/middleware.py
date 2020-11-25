"""
The core application: middleware definitions for request/response cycle.
"""
from eligibility_verification.settings import DEBUG

from . import models


class DebugMiddleware():
    """Middleware to configure debug context in the request session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.session["debug"] = DEBUG
        return self.get_response(request)

    def process_template_response(self, request, response):
        if response.context_data is None:
            response.context_data = {}
        response.context_data["debug"] = DEBUG

        if DEBUG:
            try:
                agency = models.TransitAgency.objects.get(id=request.session["agency"]).slug
            except models.TransitAgency.DoesNotExist:
                agency = "None"
            response.context_data["agency"] = agency

        return response
