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
            "required": verifier.is_auth_required,
            "logged_in": session.logged_in(request),
            "supports_sign_out": verifier.supports_sign_out,
            "sign_out_route": reverse("oauth:logout"),
        }

        if verifier.is_auth_required:
            auth_provider = verifier.auth_provider
            data["sign_out_button_label"] = auth_provider.sign_out_button_label

        return {"authentication": data}
    else:
        return {}


def debug(request):
    """Context processor adds debug information to request context."""
    return {"debug": session.context_dict(request)}


def origin(request):
    """Context processor adds session.origin to request context."""
    origin = session.origin(request)

    if origin:
        return {"origin": origin}
    else:
        return {}
