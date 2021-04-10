"""
The core application: context processors for enriching request context data.
"""
from benefits.settings import ANALYTICS_KEY

from . import session


def analytics(request):
    """Context processor adds some analytics information to request context."""
    return {"analytics": {"api_key": ANALYTICS_KEY, "uid": session.uid(request), "did": session.did(request)}}


def debug(request):
    """Context processor adds debug information to request context."""
    return {"debug": session.context_dict(request)}
