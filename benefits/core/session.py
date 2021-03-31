"""
The core application: helpers to work with request sessions.
"""
import logging
import time

from django.urls import reverse

from . import models


logger = logging.getLogger(__name__)


_AGENCY = "agency"
_DEBUG = "debug"
_ELIGIBILITY = "eligibility"
_LANG = "lang"
_ORIGIN = "origin"
_TOKEN = "token"
_TOKEN_EXP = "token_exp"


def agency(request):
    """Get the agency from the request's session, or None"""
    logger.debug("Get session agency")
    try:
        return models.TransitAgency.by_id(request.session[_AGENCY])
    except (KeyError, models.TransitAgency.DoesNotExist):
        logger.info("Can't get agency from session")
        return None


def active_agency(request):
    """True if the request's session is configured with an active agency. False otherwise."""
    logger.debug("Get session active agency flag")
    a = agency(request)
    return a and a.active


def context_dict(request):
    """The request's session context as a dict."""
    logger.debug("Get session context dict")
    return {
        _AGENCY: agency(request).slug if active_agency(request) else None,
        _DEBUG: debug(request),
        _ELIGIBILITY: ", ".join(eligibility(request)),
        _LANG: language(request),
        _ORIGIN: origin(request),
        _TOKEN: token(request),
        _TOKEN_EXP: token_expiry(request),
    }


def debug(request):
    """Get the DEBUG flag from the request's session, or None."""
    logger.debug("Get session debug flag")
    try:
        return request.session[_DEBUG]
    except KeyError:
        return None


def eligibility(request):
    """Get the list of confirmed eligibility types from the request's session, or []"""
    logger.debug("Get session confirmed eligibility")
    try:
        return (request.session[_ELIGIBILITY] or "").split(", ")
    except KeyError:
        return []


def eligible(request):
    """True if the request's session is configured with an active agency and has confirmed eligibility. False otherwise."""
    logger.debug("Get session eligible flag")
    a = agency(request)
    e = eligibility(request)
    return active_agency(request) and len(e) > 0 and set(e).issubset(a.eligibility_set)


def language(request):
    """Get the language configured for the request."""
    logger.debug("Get session language")
    return request.LANGUAGE_CODE


def origin(request):
    """Get the origin for the request's session, or None."""
    logger.debug("Get session origin")
    try:
        return request.session[_ORIGIN]
    except KeyError:
        return None


def reset(request):
    """Reset the session for the request."""
    logger.info("Reset session")
    request.session[_AGENCY] = None
    request.session[_ELIGIBILITY] = None
    request.session[_ORIGIN] = reverse("core:index")
    request.session[_TOKEN] = None
    request.session[_TOKEN_EXP] = None


def token(request):
    """Get the token from the request's session, or None."""
    logger.info("Get session token")
    try:
        return request.session[_TOKEN]
    except KeyError:
        return None


def token_expiry(request):
    """Get the token's expiry time from the request's session, or None."""
    logger.info("Get session token expiry")
    try:
        return request.session[_TOKEN_EXP]
    except KeyError:
        return None


def update(request, agency=None, debug=None, eligibility_types=None, origin=None, token=None, token_exp=None):
    """Update the request's session with non-null values."""
    if agency is not None and isinstance(agency, models.TransitAgency):
        logger.info(f"Update session {_AGENCY}")
        request.session[_AGENCY] = agency.id
    if debug is not None:
        logger.info(f"Update session {_DEBUG}")
        request.session[_DEBUG] = debug
    if eligibility_types is not None and (isinstance(eligibility_types, list) or isinstance(eligibility_types, str)):
        logger.info(f"Update session {_ELIGIBILITY}")
        eligibility_types = eligibility_types.split(", ") if isinstance(eligibility_types, str) else eligibility_types
        request.session[_ELIGIBILITY] = ", ".join(eligibility_types)
    if origin is not None:
        logger.info(f"Update session {_ORIGIN}")
        request.session[_ORIGIN] = origin
    if token is not None:
        logger.info(f"Update session {_TOKEN}")
        request.session[_TOKEN] = token
        request.session[_TOKEN_EXP] = token_exp


def valid_token(request):
    """True if the request's session is configured with a valid token. False otherwise."""
    if token(request) is not None:
        logger.info("Session contains a token")
        exp = token_expiry(request)

        # ensure token does not expire in the next 5 seconds
        valid = exp is None or exp > (time.time() + 5)

        logger.info(f"Session token is {'valid' if valid else 'expired'}")
        return valid
    else:
        logger.info("Session does not contain a valid token")
        return False
