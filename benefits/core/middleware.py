"""
The core application: middleware definitions for request/response cycle.
"""
import logging

from django.utils.deprecation import MiddlewareMixin

from benefits.settings import DEBUG
from . import analytics, session


logger = logging.getLogger(__name__)


class AgencySessionRequired(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking an agency configuration."""

    # Django 1.9 and older method signature needed for decorators
    # https://docs.djangoproject.com/en/3.1/ref/utils/#django.utils.decorators.decorator_from_middleware
    def process_request(self, request):
        if session.active_agency(request):
            logger.debug("Session configured with agency")
            return None
        else:
            raise AttributeError("Session not configured with agency")


class DebugSession:
    """Middleware to configure debug context in the request session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session.update(request, debug=DEBUG)
        return self.get_response(request)


class PageviewEvent(MiddlewareMixin):
    """Middleware sends an analytics event for pageviews."""

    # Django 1.9 and older method signature needed for decorators
    # https://docs.djangoproject.com/en/3.1/ref/utils/#django.utils.decorators.decorator_from_middleware
    def process_request(self, request):
        kwargs = dict(path=request.path, referer=request.headers.get("referer"))
        analytics.send_event(request=request, event_type="pageview", **kwargs)
        return None
