import logging

from django.conf import settings

from benefits.core import analytics

from . import recaptcha, session
from .middleware import user_error

logger = logging.getLogger(__name__)


class AgencySessionRequiredMixin:
    """Mixin intended for use with a class-based view as the first in the MRO.

    Gets the active `TransitAgency` out of session and sets an attribute on `self`.

    If the session is not configured with an agency, return a user error.
    """

    def dispatch(self, request, *args, **kwargs):
        if session.active_agency(request):
            self.agency = session.agency(request)
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.warning("Session not configured with an active agency")
            return user_error(request)


class EligibleSessionRequiredMixin:
    """Mixin intended for use with a class-based view as the first in the MRO.

    If the session is not marked as eligible (e.g. the user has verified their eligibility), return a user error.
    """

    def dispatch(self, request, *args, **kwargs):
        if session.eligible(request):
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.warning("Session does not have verified eligibility")
            return user_error(request)


class FlowSessionRequiredMixin:
    """Mixin intended for use with a class-based view as the first in the MRO.

    Gets the current `EnrollmentFlow` out of session and sets an attribute on `self`.

    If the session is not configured with a flow, return a user error.
    """

    def dispatch(self, request, *args, **kwargs):
        flow = session.flow(request)
        if flow:
            self.flow = flow
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.warning("Session not configured with enrollment flow")
            return user_error(request)


class PageViewMixin:
    """
    Mixin sends an analytics event for page views.
    """

    def dispatch(self, request, *args, **kwargs):
        event = analytics.ViewedPageEvent(request)
        try:
            analytics.send_event(event)
        except Exception:
            logger.warning(f"Failed to send event: {event}")
        finally:
            return super().dispatch(request, *args, **kwargs)


class RecaptchaEnabledMixin:
    """Mixin intended for use with a class-based view as the first in the MRO.

    Configures the request with required reCAPTCHA settings."""

    def dispatch(self, request, *args, **kwargs):
        if settings.RECAPTCHA_ENABLED:
            request.recaptcha = {
                "data_field": recaptcha.DATA_FIELD,
                "script_api": settings.RECAPTCHA_API_KEY_URL,
                "site_key": settings.RECAPTCHA_SITE_KEY,
            }
        return super().dispatch(request, *args, **kwargs)
