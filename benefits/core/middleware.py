"""
The core application: middleware definitions for request/response cycle.
"""
import logging

from django.utils.decorators import decorator_from_middleware_with_args
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

    def __init__(self, get_response, page_name):
        super().__init__(get_response)
        # the value sent via Analyics API
        self.page_name = page_name

    # Django 1.9 and older method signature needed for decorators
    # https://docs.djangoproject.com/en/3.1/ref/utils/#django.utils.decorators.decorator_from_middleware
    def process_request(self, request):
        event = analytics.PageviewEvent(request, self.page_name)
        try:
            analytics.send_event(event)
        except Exception:
            logger.warning(f"Failed to send event: {event}")
        finally:
            return None


pageview_decorator = decorator_from_middleware_with_args(PageviewEvent)
