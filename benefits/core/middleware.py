"""
The core application: middleware definitions for request/response cycle.
"""
import logging

from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareMixin
from django.views import i18n

from benefits.settings import DEBUG
from . import analytics, session


logger = logging.getLogger(__name__)


class AgencySessionRequired(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking an agency configuration."""

    def process_request(self, request):
        if session.active_agency(request):
            logger.debug("Session configured with agency")
            return None
        else:
            raise AttributeError("Session not configured with agency")


class DebugSession(MiddlewareMixin):
    """Middleware to configure debug context in the request session."""

    def process_request(self, request):
        session.update(request, debug=DEBUG)
        return None


class Healthcheck:
    """Middleware intercepts and accepts /healthcheck requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/healthcheck":
            return HttpResponse("Healthy", content_type="text/plain")
        return self.get_response(request)


class ViewedPageEvent(MiddlewareMixin):
    """Middleware sends an analytics event for page views."""

    def process_response(self, request, response):
        event = analytics.ViewedPageEvent(request)
        try:
            analytics.send_event(event)
        except Exception:
            logger.warning(f"Failed to send event: {event}")
        finally:
            return response


pageview_decorator = decorator_from_middleware(ViewedPageEvent)


class ChangedLanguageEvent(MiddlewareMixin):
    """Middleware hooks into django.views.i18n.set_language to send an analytics event."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func == i18n.set_language:
            new_lang = request.POST["language"]
            event = analytics.ChangedLanguageEvent(request, new_lang)
            analytics.send_event(event)
        return None
