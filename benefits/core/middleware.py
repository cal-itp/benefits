"""
The core application: middleware definitions for request/response cycle.
"""
import logging

from django.utils.decorators import decorator_from_middleware_with_args
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


class DebugSession:
    """Middleware to configure debug context in the request session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session.update(request, debug=DEBUG)
        return self.get_response(request)


class ViewPageEvent(MiddlewareMixin):
    """Middleware sends an analytics event for pageviews."""

    def __init__(self, get_response, page_name):
        super().__init__(get_response)
        # the value sent via Analyics API
        self.page_name = page_name

    def process_request(self, request):
        event = analytics.ViewPageEvent(request, self.page_name)
        try:
            analytics.send_event(event)
        except Exception:
            logger.warning(f"Failed to send event: {event}")
        finally:
            return None


pageview_decorator = decorator_from_middleware_with_args(ViewPageEvent)


class ChangeLanguageEvent:
    """Middleware hooks into django.views.i18n.set_language to send an analytics event."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func == i18n.set_language:
            new_lang = request.POST["language"]
            event = analytics.ChangeLanguageEvent(request, new_lang)
            analytics.send_event(event)
        return None
