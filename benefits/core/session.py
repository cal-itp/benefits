"""
The core application: helpers to work with request sessions.
"""

import hashlib
import logging
import time
import uuid
from datetime import datetime, timedelta, timezone

from cdt_identity.claims import ClaimsResult
from cdt_identity.session import Session as OAuthSession
from django.urls import reverse

from benefits.enrollment_littlepay.models import LittlepayGroup
from benefits.enrollment_littlepay.session import Session as LittlepaySession
from benefits.enrollment_switchio.models import SwitchioGroup
from benefits.enrollment_switchio.session import Session as SwitchioSession
from benefits.routes import routes

from . import models

logger = logging.getLogger(__name__)


_AGENCY = "agency"
_DEBUG = "debug"
_DID = "did"
_ELIGIBLE = "eligibility"
_ENROLLMENT_EXP = "enrollment_expiry"
_FLOW = "flow"
_GROUP = "group"  # EnrollmentGroup, not django.auth Group
_LANG = "lang"
_LOGGED_IN = "logged_in"
_ORIGIN = "origin"
_START = "start"
_UID = "uid"


def agency(request):
    """Get the agency from the request's session, or None"""
    try:
        return models.TransitAgency.by_id(request.session[_AGENCY])
    except (KeyError, models.TransitAgency.DoesNotExist):
        return None


def active_agency(request):
    """True if the request's session is configured with an active agency. False otherwise."""
    a = agency(request)
    return a and a.active


def context_dict(request):
    """The request's session context as a dict."""
    littlepay_session = LittlepaySession(request)
    switchio_session = SwitchioSession(request)
    return {
        _AGENCY: agency(request).slug if active_agency(request) else None,
        _DEBUG: debug(request),
        _DID: did(request),
        _FLOW: flow(request),
        _GROUP: group(request),
        _ELIGIBLE: eligible(request),
        _ENROLLMENT_EXP: enrollment_expiry(request),
        littlepay_session._keys_access_token: littlepay_session.access_token,
        littlepay_session._keys_access_token_expiry: littlepay_session.access_token_expiry,
        switchio_session._keys_registration_id: switchio_session.registration_id,
        _LANG: language(request),
        _LOGGED_IN: logged_in(request),
        _ORIGIN: origin(request),
        _START: start(request),
        _UID: uid(request),
    }


def debug(request):
    """Get the DEBUG flag from the request's session."""
    return bool(request.session.get(_DEBUG, False))


def did(request):
    """
    Get the session's device ID, a hashed version of the unique ID. If unset,
    the session is reset to initialize a value.

    This value, like UID, is randomly generated per session and is needed for
    Amplitude to accurately track that a sequence of events came from a unique
    user.

    See more: https://help.amplitude.com/hc/en-us/articles/115003135607-Track-unique-users-in-Amplitude
    """
    d = request.session.get(_DID)
    if not d:
        reset(request)
        d = request.session.get(_DID)
    return str(d)


def eligible(request):
    """True if the request's session has confirmed eligibility. False otherwise."""
    return request.session.get(_ELIGIBLE)


def enrollment_expiry(request):
    """Get the expiry date for a user's enrollment from session, or None."""
    expiry = request.session.get(_ENROLLMENT_EXP)
    if expiry:
        return datetime.fromtimestamp(expiry, tz=timezone.utc)
    else:
        return None


def enrollment_reenrollment(request):
    """Get the reenrollment date for a user's enrollment from session, or None."""
    expiry = enrollment_expiry(request)
    enrollment_flow = flow(request)

    if enrollment_flow and enrollment_flow.supports_expiration and expiry:
        return expiry - timedelta(days=enrollment_flow.expiration_reenrollment_days)
    else:
        return None


def flow(request) -> models.EnrollmentFlow | None:
    """Get the EnrollmentFlow from the request's session, or None"""
    try:
        return models.EnrollmentFlow.by_id(request.session[_FLOW])
    except (KeyError, models.EnrollmentFlow.DoesNotExist):
        return None


def group(request) -> models.EnrollmentGroup | None:
    """Get the EnrollmentGroup from the request's session, or None"""

    if agency(request):
        match agency(request).transit_processor:
            case "littlepay":
                group_model = LittlepayGroup
            case "switchio":
                group_model = SwitchioGroup
            case _:
                return None

        try:
            return group_model.by_id(request.session[_GROUP])
        except (KeyError, group_model.DoesNotExist):
            return None

    return None


def language(request):
    """Get the language configured for the request."""
    return request.LANGUAGE_CODE


def logged_in(request):
    """Get the user's status of having logged in with OAuth from the request's session, or None"""
    return bool(request.session.get(_LOGGED_IN))


def logout(request):
    """Reset the session claims and tokens."""
    LittlepaySession(request, reset=True)
    SwitchioSession(request, reset=True)
    OAuthSession(request, claims_result=ClaimsResult())
    update(request, logged_in=False)


def oauth_extra_claims(request):
    """Get the extra oauth claims from the request's session, or None"""
    claims = [claim for claim, value in OAuthSession(request).claims_result.verified.items() if value]

    if claims:
        f = flow(request)
        if f and f.uses_claims_verification:
            claims.remove(f.claims_request.eligibility_claim)
            return claims or None
        raise Exception("Oauth claims but no flow")
    else:
        return None


def origin(request):
    """Get the origin for the request's session, or default to the index route."""
    return request.session.get(_ORIGIN, reverse(routes.INDEX))


def reset(request):
    """Reset the session for the request."""
    logger.debug("Reset session")
    request.session[_AGENCY] = None
    request.session[_FLOW] = None
    request.session[_GROUP] = None
    request.session[_ELIGIBLE] = False
    request.session[_ORIGIN] = reverse(routes.INDEX)
    request.session[_ENROLLMENT_EXP] = None
    request.session[_LOGGED_IN] = False
    LittlepaySession(request, reset=True)
    SwitchioSession(request, reset=True)
    OAuthSession(request, reset=True)

    if _UID not in request.session or not request.session[_UID]:
        logger.debug("Reset session time and uid")
        request.session[_START] = int(time.time() * 1000)
        u = str(uuid.uuid4())
        request.session[_UID] = u
        request.session[_DID] = str(uuid.UUID(hashlib.sha512(bytes(u, "utf8")).hexdigest()[:32]))


def start(request):
    """
    Get the start time from the request's session, as integer milliseconds since
    Epoch. If unset, the session is reset to initialize a value.

    Once started, does not reset after subsequent calls to session.reset() or
    session.start(). This value is needed for Amplitude to accurately track
    sessions.

    See more: https://help.amplitude.com/hc/en-us/articles/115002323627-Tracking-Sessions
    """
    s = request.session.get(_START)
    if not s:
        reset(request)
        s = request.session.get(_START)
    return s


def uid(request):
    """
    Get the session's unique ID, a randomly generated UUID4 string. If unset,
    the session is reset to initialize a value.

    This value, like DID, is needed for Amplitude to accurately track that a
    sequence of events came from a unique user.

    See more: https://help.amplitude.com/hc/en-us/articles/115003135607-Track-unique-users-in-Amplitude

    Although Amplitude advises *against* setting user_id for anonymous users,
    here a value is set on anonymous users anyway, as the users never sign-in
    and become de-anonymized to this app / Amplitude.
    """
    u = request.session.get(_UID)
    if not u:
        reset(request)
        u = request.session.get(_UID)
    return u


def update(
    request,
    agency=None,
    debug=None,
    flow=None,
    group=None,
    eligible=None,
    enrollment_expiry=None,
    logged_in=None,
    origin=None,
):
    """Update the request's session with non-null values."""
    if agency is not None and isinstance(agency, models.TransitAgency):
        request.session[_AGENCY] = agency.id
    if debug is not None:
        request.session[_DEBUG] = debug
    if eligible is not None:
        request.session[_ELIGIBLE] = bool(eligible)
    if isinstance(enrollment_expiry, datetime):
        if enrollment_expiry.tzinfo is None or enrollment_expiry.tzinfo.utcoffset(enrollment_expiry) is None:
            # this is a naive datetime instance, update tzinfo for UTC
            # see notes under https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
            # > There is no method to obtain the POSIX timestamp directly from a naive datetime instance representing UTC time.
            # > If your application uses this convention and your system timezone is not set to UTC, you can obtain the POSIX
            # > timestamp by supplying tzinfo=timezone.utc
            enrollment_expiry = enrollment_expiry.replace(tzinfo=timezone.utc)
        request.session[_ENROLLMENT_EXP] = enrollment_expiry.timestamp()
    if logged_in is not None:
        request.session[_LOGGED_IN] = logged_in
    if origin is not None:
        request.session[_ORIGIN] = origin
    if flow is not None and isinstance(flow, models.EnrollmentFlow):
        request.session[_FLOW] = flow.id
        oauth_session = OAuthSession(request)
        oauth_session.client_config = flow.oauth_config
        oauth_session.claims_request = flow.claims_request
    if group is not None and isinstance(group, models.EnrollmentGroup):
        request.session[_GROUP] = group.id
