"""
The core application: helpers to work with request sessions.
"""
import hashlib
import logging
import time
import uuid

from django.urls import reverse

from benefits.settings import RATE_LIMIT_PERIOD
from . import models


logger = logging.getLogger(__name__)


_AGENCY = "agency"
_DEBUG = "debug"
_DID = "did"
_ELIGIBILITY = "eligibility"
_ENROLLMENT_TOKEN = "enrollment_token"
_ENROLLMENT_TOKEN_EXP = "enrollment_token_exp"
_LANG = "lang"
_LIMITCOUNTER = "limitcounter"
_LIMITUNTIL = "limituntil"
_OAUTH_TOKEN = "oauth_token"
_ORIGIN = "origin"
_START = "start"
_UID = "uid"
_VERIFIER = "verifier"


def agency(request):
    """Get the agency from the request's session, or None"""
    logger.debug("Get session agency")
    try:
        return models.TransitAgency.by_id(request.session[_AGENCY])
    except (KeyError, models.TransitAgency.DoesNotExist):
        logger.debug("Can't get agency from session")
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
        _LIMITCOUNTER: rate_limit_counter(request),
        _DEBUG: debug(request),
        _DID: did(request),
        _ELIGIBILITY: eligibility(request),
        _ENROLLMENT_TOKEN: enrollment_token(request),
        _ENROLLMENT_TOKEN_EXP: enrollment_token_expiry(request),
        _LANG: language(request),
        _OAUTH_TOKEN: oauth_token(request),
        _ORIGIN: origin(request),
        _LIMITUNTIL: rate_limit_time(request),
        _START: start(request),
        _UID: uid(request),
        _VERIFIER: verifier(request),
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


def enrollment_token(request):
    """Get the enrollment token from the request's session, or None."""
    logger.debug("Get session enrollment token")
    return request.session.get(_ENROLLMENT_TOKEN)


def enrollment_token_expiry(request):
    """Get the enrollment token's expiry time from the request's session, or None."""
    logger.debug("Get session enrollment token expiry")
    return request.session.get(_ENROLLMENT_TOKEN_EXP)


def increment_rate_limit_counter(request):
    """Adds 1 to this session's rate limit counter."""
    logger.debug("Increment rate limit counter")
    c = rate_limit_counter(request)
    request.session[_LIMITCOUNTER] = int(c) + 1


def language(request):
    """Get the language configured for the request."""
    logger.debug("Get session language")
    return request.LANGUAGE_CODE


def oauth_token(request):
    """Get the oauth token from the request's session, or None"""
    logger.debug("Get session oauth token")
    return request.session.get(_OAUTH_TOKEN)


def origin(request):
    """Get the origin for the request's session, or None."""
    logger.debug("Get session origin")
    return request.session.get(_ORIGIN)


def rate_limit_counter(request):
    """Get this session's rate limit counter."""
    logger.debug("Get rate limit counter")
    return request.session.get(_LIMITCOUNTER)


def rate_limit_time(request):
    """Get this session's rate limit time, a Unix timestamp after which the session's rate limt resets."""
    logger.debug("Get rate limit time")
    return request.session.get(_LIMITUNTIL)


def reset(request):
    """Reset the session for the request."""
    logger.debug("Reset session")
    request.session[_AGENCY] = None
    request.session[_ELIGIBILITY] = None
    request.session[_ORIGIN] = reverse("core:index")
    request.session[_ENROLLMENT_TOKEN] = None
    request.session[_ENROLLMENT_TOKEN_EXP] = None
    request.session[_OAUTH_TOKEN] = None
    request.session[_VERIFIER] = None

    if _UID not in request.session or not request.session[_UID]:
        logger.debug("Reset session time and uid")
        request.session[_START] = int(time.time() * 1000)
        u = str(uuid.uuid4())
        request.session[_UID] = u
        request.session[_DID] = str(uuid.UUID(hashlib.sha512(bytes(u, "utf8")).hexdigest()[:32]))
        reset_rate_limit(request)


def reset_rate_limit(request):
    """Reset this session's rate limit counter and time."""
    logger.debug("Reset rate limit")
    request.session[_LIMITCOUNTER] = 0
    # get the current time in Unix seconds, then add RATE_LIMIT_PERIOD seconds
    request.session[_LIMITUNTIL] = int(time.time()) + RATE_LIMIT_PERIOD


def start(request):
    """Get the start time from the request's session, as integer milliseconds since Epoch."""
    logger.debug("Get session time")
    s = request.session.get(_START)
    if not s:
        reset(request)
        s = request.session.get(_START)
    return s


def uid(request):
    """Get the session's unique ID, generating a new one if necessary."""
    logger.debug("Get session uid")
    u = request.session.get(_UID)
    if not u:
        reset(request)
        u = request.session.get(_UID)
    return u


def update(
    request,
    agency=None,
    debug=None,
    eligibility_types=None,
    enrollment_token=None,
    enrollment_token_exp=None,
    oauth_token=None,
    origin=None,
    verifier=None,
):
    """Update the request's session with non-null values."""
    if agency is not None and isinstance(agency, models.TransitAgency):
        logger.debug(f"Update session {_AGENCY}")
        request.session[_AGENCY] = agency.id
    if debug is not None:
        logger.debug(f"Update session {_DEBUG}")
        request.session[_DEBUG] = debug
    if eligibility_types is not None and isinstance(eligibility_types, list):
        logger.debug(f"Update session {_ELIGIBILITY}")
        if len(eligibility_types) > 1:
            raise NotImplementedError("Multiple eligibilities are not supported at this time.")
        elif len(eligibility_types) == 1:
            # get the eligibility corresponding to the session's agency
            a = models.TransitAgency.by_id(request.session[_AGENCY])
            t = str(eligibility_types[0]).strip()
            request.session[_ELIGIBILITY] = a.get_type_id(t)
        else:
            # empty list, clear session eligibility
            request.session[_ELIGIBILITY] = None
    if enrollment_token is not None:
        logger.debug(f"Update session {_ENROLLMENT_TOKEN}")
        request.session[_ENROLLMENT_TOKEN] = enrollment_token
        request.session[_ENROLLMENT_TOKEN_EXP] = enrollment_token_exp
    if oauth_token is not None:
        logger.debug(f"Update session {_OAUTH_TOKEN}")
        request.session[_OAUTH_TOKEN] = oauth_token
    if origin is not None:
        logger.debug(f"Update session {_ORIGIN}")
        request.session[_ORIGIN] = origin
    if verifier is not None and isinstance(verifier, models.EligibilityVerifier):
        logger.debug(f"Update session {_VERIFIER}")
        request.session[_VERIFIER] = verifier.id


def valid_enrollment_token(request):
    """True if the request's session is configured with a valid token. False otherwise."""
    if enrollment_token(request) is not None:
        logger.debug("Session contains an enrollment token")
        exp = enrollment_token_expiry(request)

        # ensure token does not expire in the next 5 seconds
        valid = exp is None or exp > (time.time() + 5)

        logger.debug(f"Session enrollment token is {'valid' if valid else 'expired'}")
        return valid
    else:
        logger.debug("Session does not contain a valid enrollment token")
        return False


def verifier(request):
    """Get the verifier from the request's session, or None"""
    logger.debug("Get session verifier")
    try:
        return models.EligibilityVerifier.by_id(request.session[_VERIFIER])
    except (KeyError, models.EligibilityVerifier.DoesNotExist):
        logger.debug("Can't get verifier from session")
        return None
