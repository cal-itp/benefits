"""
The core application: context processors for enriching request context data.
"""

from django.conf import settings

from benefits.routes import Routes, routes as app_routes

from . import models, session


def unique_values(original_list):
    # dict.fromkeys gets the unique values and preserves order
    return list(dict.fromkeys(original_list))


def _agency_context(agency: models.TransitAgency):
    return {
        "eligibility_index_url": agency.eligibility_index_url,
        "help_templates": unique_values([f.help_template for f in agency.enrollment_flows.all() if f.help_template]),
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
    flow = session.flow(request)

    if flow:
        data = {
            "logged_in": session.logged_in(request),
        }

        if flow.uses_claims_verification:
            data["sign_out_button_template"] = flow.claims_provider.sign_out_button_template
            data["sign_out_link_template"] = flow.claims_provider.sign_out_link_template

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


def origin(request):
    """Context processor adds session.origin to request context."""
    origin = session.origin(request)

    if origin:
        return {"origin": origin}
    else:
        return {}


def routes(request):
    """Context processor adds information about each application route to the context."""

    # get a dict[str,str] mapping property name --> value
    # for each @property in the Routes collection
    routes_dict = dict(
        (prop, str(getattr(app_routes, prop)))
        for prop in dir(app_routes)
        if prop not in dir(Routes) or isinstance(getattr(Routes, prop), property)
    )

    return {"routes": routes_dict}
