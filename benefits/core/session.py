"""
The core application: helpers to work with request sessions.
"""
import hashlib
import logging
import time
import uuid

from django.urls import reverse

from . import models


logger = logging.getLogger(__name__)


_AGENCY = "agency"
_DEBUG = "debug"
_DID = "did"
_ELIGIBILITY = "eligibility"
_LANG = "lang"
_ORIGIN = "origin"
_START = "start"
_UID = "uid"

# ignore bandit B105:hardcoded_password_string
# as these are not passwords, but keys for the session dict
_TOKEN = "token"  # nosec
_TOKEN_EXP = "token_exp"  # nosec


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
        _DID: did(request),
        _ELIGIBILITY: eligibility(request),
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


def did(request):
    """Get the session's device ID, a hashed version of the unique ID."""
    logger.debug("Get session did")
    d = request.session.get(_DID)
    if not d:
        reset(request)
        d = request.session.get(_DID)
    return str(d)


def eligibility(request):
    """Get the confirmed models.EligibilityType from the request's session, or None"""
    logger.debug("Get session confirmed eligibility")
    eligibility = request.session.get(_ELIGIBILITY)
    if eligibility:
        return models.EligibilityType.get(eligibility)
    else:
        return None


def eligible(request):
    """True if the request's session is configured with an active agency and has confirmed eligibility. False otherwise."""
    logger.debug("Get session eligible flag")
    return active_agency(request) and agency(request).supports_type(eligibility(request))


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
        u = str(uuid.uuid4())
        request.session[_UID] = u
        request.session[_DID] = str(uuid.UUID(hashlib.sha512(bytes(u, "utf8")).hexdigest()[:32]))


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
    """Get the session's unique ID, generating a new one if necessary."""
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
    if eligibility_types is not None and isinstance(eligibility_types, list):
        logger.info(f"Update session {_ELIGIBILITY}")
        if len(eligibility_types) > 1:
            raise NotImplementedError("Multiple eligibilities are not supported at this time.")
        elif len(eligibility_types) == 1:
            # get the eligibility corresponding to the session's agency
            a = models.TransitAgency.by_id(request.session[_AGENCY])
            t = str(eligibility_types[0]).strip()
            request.session[_ELIGIBILITY] = a.get_type_id(t)
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
