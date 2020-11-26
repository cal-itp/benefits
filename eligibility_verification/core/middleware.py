"""
The core application: middleware definitions for request/response cycle.
"""
from django.utils.deprecation import MiddlewareMixin

from eligibility_verification.settings import DEBUG

from . import models


class AgencyRequiredMiddleware(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking an agency configuration."""

    # Django 1.9 and older method signature needed for decorators
    # https://docs.djangoproject.com/en/3.1/ref/utils/#django.utils.decorators.decorator_from_middleware
    def process_view(self, request, view_func, view_args, view_kwargs):
        if ("agency" in request.session and
            request.session["agency"] is not None and
            models.TransitAgency.by_id(request.session["agency"]).active
        ):
            return None
        else:
            raise AttributeError("Agency not configured for session")


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
