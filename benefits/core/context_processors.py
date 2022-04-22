"""
The core application: context processors for enriching request context data.
"""
from django.conf import settings

from . import session


def analytics(request):
    """Context processor adds some analytics information to request context."""
    return {"analytics": {"api_key": settings.ANALYTICS_KEY, "uid": session.uid(request), "did": session.did(request)}}


def debug(request):
    """Context processor adds debug information to request context."""
    return {"debug": session.context_dict(request)}


def recaptcha(request):
    """Context processor adds recaptcha information to request context."""
    return {
        "recaptcha": {
            "api_url": settings.RECAPTCHA_API_URL,
            "enabled": settings.RECAPTCHA_ENABLED,
            "site_key": settings.RECAPTCHA_SITE_KEY,
        }
    }
