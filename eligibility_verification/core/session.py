"""
The core application: helpers to work with request sessions.
"""
from django.urls import reverse

from . import models


_AGENCY = "agency"
_DEBUG = "debug"
_ELIGIBILITY = "eligibility"
_ORIGIN = "origin"


def reset(request):
    """Reset the session for the request."""
    request.session[_AGENCY] = None
    request.session[_DEBUG] = None
    request.session[_ELIGIBILITY] = None
    request.session[_ORIGIN] = reverse("core:index")


def update(request, agency=None, debug=None, eligibility=None, origin=None):
    """Update the request's session."""
    if agency is not None:
        request.session[_AGENCY] = agency.id
    if debug is not None:
        request.session[_DEBUG] = debug
    if eligibility is not None:
        request.session[_ELIGIBILITY] = eligibility
    if origin is not None:
        request.session[_ORIGIN] = origin


def agency(request):
    """Get the agency from the request's session."""
    try:
        return models.TransitAgency.by_id(request.session[_AGENCY])
    except (KeyError, models.TransitAgency.DoesNotExist):
        return None


def active_agency(request):
    """True if the request's session is configured with an active agency. False otherwise."""
    a = agency(request)
    return a and a.active


def origin(request):
    """Get the origin for the request."""
    return request.session[_ORIGIN]
