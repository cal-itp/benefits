"""
The core application: middleware definitions for request/response cycle.
"""
import logging

import time

from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareMixin
from django.views import i18n

from benefits.settings import RATE_LIMIT, RATE_LIMIT_METHODS, RATE_LIMIT_PERIOD, DEBUG
from . import analytics, session, viewmodels


logger = logging.getLogger(__name__)


class AgencySessionRequired(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking an agency configuration."""

    def process_request(self, request):
        if session.active_agency(request):
            logger.debug("Session configured with agency")
            return None
        else:
            raise AttributeError("Session not configured with agency")


class RateLimit(MiddlewareMixin):
    """Middleware checks settings and session to ensure rate limit is respected."""

    def process_request(self, request):
        if any((RATE_LIMIT < 1, len(RATE_LIMIT_METHODS) < 1, RATE_LIMIT_PERIOD < 1)):
            logger.debug("RATE_LIMIT, RATE_LIMIT_METHODS, or RATE_LIMIT_PERIOD are not configured")
            return None

        if request.method in RATE_LIMIT_METHODS:
            session.increment_rate_limit_counter(request)
        else:
            # bail early if the request method doesn't match
            return None

        counter = session.rate_limit_counter(request)
        reset_time = session.rate_limit_time(request)
        now = int(time.time())

        if counter > RATE_LIMIT:
            if reset_time > now:
                logger.warn("Rate limit exceeded")
                home = viewmodels.Button.home(request)
                page = viewmodels.ErrorPage.error(
                    title="Rate limit error",
                    content_title="Rate limit error",
                    paragraphs=["You have reached the rate limit. Please try again."],
                    button=home,
                )
                t = loader.get_template("400.html")
                return HttpResponseBadRequest(t.render(page.context_dict()))
            else:
                # enough time has passed, reset the rate limit
                session.reset_rate_limit(request)

        return None


class EligibleSessionRequired(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking confirmed eligibility."""

    def process_request(self, request):
        if session.eligible(request):
            logger.debug("Session has confirmed eligibility")
            return None
        else:
            raise AttributeError("Session has no confirmed eligibility")


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
