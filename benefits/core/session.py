"""
The core application: helpers to work with request sessions.
"""
import logging
import time
import uuid

from django.urls import reverse

from . import models


logger = logging.getLogger(__name__)


_AGENCY = "agency"
_DEBUG = "debug"
_ELIGIBILITY = "eligibility"
_LANG = "lang"
_ORIGIN = "origin"
_START = "start"
_TOKEN = "token"
_TOKEN_EXP = "token_exp"
_UID = "uid"


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
        _START: start(request),
        _TOKEN: token(request),
        _TOKEN_EXP: token_expiry(request),
        _UID: uid(request),
    }


def debug(request):
    """Get the DEBUG flag from the request's session."""
    logger.debug("Get session debug flag")
    return bool(request.session.get(_DEBUG, False))


def eligibility(request):
    """Get the list of confirmed eligibility types from the request's session, or []"""
    logger.debug("Get session confirmed eligibility")
    return (request.session.get(_ELIGIBILITY) or "").split(",")


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
    return request.session.get(_ORIGIN)


def reset(request):
    """Reset the session for the request."""
    logger.info("Reset session")
    request.session[_AGENCY] = None
    request.session[_ELIGIBILITY] = None
    request.session[_ORIGIN] = reverse("core:index")
    request.session[_TOKEN] = None
    request.session[_TOKEN_EXP] = None

    if _UID not in request.session or not request.session[_UID]:
        logger.info("Reset session time and uid")
        request.session[_START] = int(time.time() * 1000)
        request.session[_UID] = str(uuid.uuid4())


def start(request):
    """Get the start time from the request's session, as integer milliseconds since Epoch."""
    logger.info("Get session time")
    s = request.session.get(_START)
    if not s:
        reset(request)
        s = request.session.get(_START)
    return s


def token(request):
    """Get the token from the request's session, or None."""
    logger.info("Get session token")
    return request.session.get(_TOKEN)


def token_expiry(request):
    """Get the token's expiry time from the request's session, or None."""
    logger.info("Get session token expiry")
    return request.session.get(_TOKEN_EXP)


def uid(request):
    """Get the session's unique ID, or None."""
    logger.debug("Get session uid")
    u = request.session.get(_UID)
    if not u:
        reset(request)
        u = request.session.get(_UID)
    return u


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
