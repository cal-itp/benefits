"""
The core application: context processors for enriching request context data.
"""

from django.conf import settings

from . import models, session


def unique_values(original_list):
    # dict.fromkeys gets the unique values and preserves order
    return list(dict.fromkeys(original_list))


def _agency_context(agency):
    return {
        "eligibility_index_url": agency.eligibility_index_url,
        "help_templates": unique_values(
            [v.help_template for v in agency.eligibility_verifiers.all() if v.help_template is not None]
        ),
        "info_url": agency.info_url,
        "long_name": agency.long_name,
        "phone": agency.phone,
        "short_name": agency.short_name,
        "slug": agency.slug,
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
            data["sign_out_button_template"] = verifier.auth_provider.sign_out_button_template
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
