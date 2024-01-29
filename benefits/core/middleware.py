"""
The core application: middleware definitions for request/response cycle.
"""

import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareMixin
from django.views import i18n

from . import analytics, recaptcha, session


logger = logging.getLogger(__name__)

HEALTHCHECK_PATH = "/healthcheck"
ROUTE_INDEX = "core:index"
TEMPLATE_USER_ERROR = "200-user-error.html"


def user_error(request):
    return TemplateResponse(request, TEMPLATE_USER_ERROR)


class AgencySessionRequired(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking an agency configuration."""

    def process_request(self, request):
        if session.active_agency(request):
            logger.debug("Session configured with agency")
            return None
        else:
            logger.debug("Session not configured with agency")
            return user_error(request)


class EligibleSessionRequired(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking confirmed eligibility."""

    def process_request(self, request):
        if session.eligible(request):
            logger.debug("Session has confirmed eligibility")
            return None
        else:
            logger.debug("Session has no confirmed eligibility")
            return user_error(request)


class DebugSession(MiddlewareMixin):
    """Middleware to configure debug context in the request session."""

    def process_request(self, request):
        session.update(request, debug=settings.DEBUG)
        return None


class Healthcheck:
    """Middleware intercepts and accepts /healthcheck requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == HEALTHCHECK_PATH:
            return HttpResponse("Healthy", content_type="text/plain")
        return self.get_response(request)


class HealthcheckUserAgents(MiddlewareMixin):
    """Middleware to return healthcheck for user agents specified in HEALTHCHECK_USER_AGENTS."""

    def process_request(self, request):
        if hasattr(request, "META"):
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            if user_agent in settings.HEALTHCHECK_USER_AGENTS:
                return HttpResponse("Healthy", content_type="text/plain")

        return self.get_response(request)


class VerifierSessionRequired(MiddlewareMixin):
    """Middleware raises an exception for sessions lacking an eligibility verifier configuration."""

    def process_request(self, request):
        if session.verifier(request):
            logger.debug("Session configured with eligibility verifier")
            return None
        else:
            logger.debug("Session not configured with eligibility verifier")
            return user_error(request)


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
            new_lang = request.POST.get("language")
            if new_lang:
                event = analytics.ChangedLanguageEvent(request, new_lang)
                analytics.send_event(event)
            else:
                logger.warning("i18n.set_language POST without language")
        return None


class LoginRequired(MiddlewareMixin):
    """Middleware that checks whether a user is logged in."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        # only require login if verifier requires it
        verifier = session.verifier(request)
        if not verifier or not verifier.is_auth_required or session.logged_in(request):
            # pass through
            return None

        return redirect("oauth:login")


class RecaptchaEnabled(MiddlewareMixin):
    """Middleware configures the request with required reCAPTCHA settings."""

    def process_request(self, request):
        if settings.RECAPTCHA_ENABLED:
            request.recaptcha = {
                "data_field": recaptcha.DATA_FIELD,
                "script_api": settings.RECAPTCHA_API_KEY_URL,
                "site_key": settings.RECAPTCHA_SITE_KEY,
            }
        return None


class IndexOrAgencyIndexOrigin(MiddlewareMixin):
    """Middleware sets the session.origin to either the core:index or core:agency_index depending on agency config."""

    def process_request(self, request):
        if session.active_agency(request):
            session.update(request, origin=session.agency(request).index_url)
        else:
            session.update(request, origin=reverse(ROUTE_INDEX))
        return None


index_or_agencyindex_origin_decorator = decorator_from_middleware(IndexOrAgencyIndexOrigin)
