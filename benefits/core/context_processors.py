"""
The core application: context processors for enriching request context data.
"""
from django.conf import settings

from . import models, session


def _agency_context(agency):
    return {
        "long_name": agency.long_name,
        "short_name": agency.short_name,
        "info_url": agency.info_url,
        "phone": agency.phone,
    }


def agency(request):
    """Context processor adds some information about the active agency to the request context."""
    agency = session.agency(request)

    if agency is None:
        return {}

    return {"agency": _agency_context(agency)}


def active_agencies(request):
    """Context processor adds some information about all active agencies to the request context."""
    agencies = models.TransitAgency.all_active()

    return {"active_agencies": [_agency_context(agency) for agency in agencies]}


def analytics(request):
    """Context processor adds some analytics information to request context."""
    return {"analytics": {"api_key": settings.ANALYTICS_KEY, "uid": session.uid(request), "did": session.did(request)}}


def authentication(request):
    """Context processor adds authentication information to request context."""
    verifier = session.verifier(request)

    if verifier:
        data = {
            "logged_in": session.logged_in(request),
        }

        if verifier.is_auth_required:
            data["sign_out_link_template"] = verifier.auth_provider.sign_out_link_template

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
