"""
The core application: context processors for enriching request context data.
"""

from django.conf import settings

from benefits.routes import routes as app_routes

from . import models, session


def _agency_context(agency: models.TransitAgency):
    # build up a single list of all flow help contexts
    flows_help = []
    for flow in agency.enrollment_flows.all():
        # flow.help_context is a list of context objects
        if len(flow.help_context) > 0:
            flows_help.extend(flow.help_context)

    agency_context = {
        "eligibility_index_url": agency.eligibility_index_url,
        "flows_help": flows_help,
        "info_url": agency.info_url,
        "littlepay_config": agency.littlepay_config,
        "long_name": agency.long_name,
        "phone": agency.phone,
        "short_name": agency.short_name,
        "slug": agency.slug,
        "supported_card_schemes": [
            models.CardSchemes.CHOICES.get(card_scheme) for card_scheme in agency.supported_card_schemes
        ],
        "switchio_config": agency.switchio_config,
    }

    if agency.logo_large and agency.logo_small:
        agency_context.update(
            {
                "logo_small_url": agency.logo_small.url,
                "logo_large_url": agency.logo_large.url,
            }
        )

    return agency_context


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
    flow = session.flow(request)

    if flow:
        data = {
            "logged_in": session.logged_in(request),
        }

        if flow.uses_claims_verification:
            data["sign_out_button_template"] = flow.sign_out_button_template
            data["sign_out_link_template"] = flow.sign_out_link_template

        return {"authentication": data}
    else:
        return {}


def debug(request):
    """Context processor adds debug information to request context."""
    return {"debug": session.context_dict(request)}


def enrollment(request):
    """Context processor adds enrollment information to request context."""
    flow = session.flow(request)
    expiry = session.enrollment_expiry(request)
    reenrollment = session.enrollment_reenrollment(request)

    data = {
        "expires": expiry,
        "reenrollment": reenrollment,
        "supports_expiration": flow.supports_expiration if flow else False,
    }

    return {"enrollment": data}


def feature_flags(request):
    """Context processor adds feature flags to request context."""
    return {"feature_flags": {}}


def origin(request):
    """Context processor adds session.origin to request context."""
    origin = session.origin(request)

    if origin:
        return {"origin": origin}
    else:
        return {}


def routes(request):
    """Context processor adds information about each application route to the context."""

    return {"routes": app_routes.to_dict()}
