"""
The core application: context processors for enriching request context data.
"""
from django.conf import settings
from django.urls import reverse

from . import session


def analytics(request):
    """Context processor adds some analytics information to request context."""
    return {"analytics": {"api_key": settings.ANALYTICS_KEY, "uid": session.uid(request), "did": session.did(request)}}


def authentication(request):
    """Context processor adds authentication information to request context."""
    verifier = session.verifier(request)

    if verifier:
        data = {
            "required": verifier.requires_authentication,
            "logged_in": session.logged_in(request),
            "sign_out_route": reverse("oauth:logout"),
        }

        if verifier.requires_authentication:
            auth_provider = verifier.auth_provider
            data["sign_in_button_label"] = auth_provider.sign_in_button_label
            data["sign_out_button_label"] = auth_provider.sign_out_button_label

        return {"authentication": data}
    else:
        return {}


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
