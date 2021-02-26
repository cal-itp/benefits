"""
The core application: middleware definitions for request/response cycle.
"""
from django.utils.deprecation import MiddlewareMixin

from benefits.settings import DEBUG

from . import session


class AgencySessionRequired(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking an agency configuration."""

    # Django 1.9 and older method signature needed for decorators
    # https://docs.djangoproject.com/en/3.1/ref/utils/#django.utils.decorators.decorator_from_middleware
    def process_view(self, request, view_func, view_args, view_kwargs):
        if session.active_agency(request):
            return None
        else:
            raise AttributeError("Agency not configured for session")


class DebugSession:
    """Middleware to configure debug context in the request session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session.update(request, debug=DEBUG)
        return self.get_response(request)
