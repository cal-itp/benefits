from datetime import datetime, timezone
import time

from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
import pytest

from benefits.core import models, session
from benefits.core.middleware import ROUTE_INDEX


@pytest.mark.django_db
def test_active_agency_False(app_request, model_TransitAgency_inactive):
    session.update(app_request, agency=None)

    assert not session.active_agency(app_request)

    session.update(app_request, agency=model_TransitAgency_inactive)

    assert not session.active_agency(app_request)


@pytest.mark.django_db
def test_active_agency_True(model_TransitAgency, app_request):
    assert model_TransitAgency.active
    session.update(app_request, agency=model_TransitAgency)

    assert session.active_agency(app_request)


@pytest.mark.django_db
def test_debug_default(app_request):
    debug = session.debug(app_request)

    assert isinstance(debug, bool)
    assert not debug


@pytest.mark.django_db
def test_did_default(app_request, mocker):
    # did() resets and returns a value when user is not configured
    spy = mocker.spy(session, "reset")
    app_request.session[session._DID] = None
    app_request.session[session._UID] = None

    did = session.did(app_request)

    spy.assert_called_once()
    assert did
    assert isinstance(did, str)
    assert did != "None"


@pytest.mark.django_db
def test_eligibility_default(app_request):
    assert session.eligibility(app_request) is None


@pytest.mark.django_db
def test_eligibile_False(app_request):
    agency = models.TransitAgency.objects.first()
    eligibility = []

    session.update(app_request, agency=agency, eligibility_types=eligibility)

    assert not session.eligible(app_request)


@pytest.mark.django_db
def test_eligibile_True(model_TransitAgency, app_request):
    eligibility = model_TransitAgency.eligibility_types.first()

    session.update(app_request, agency=model_TransitAgency, eligibility_types=[eligibility.name])

    assert session.eligible(app_request)


@pytest.mark.django_db
def test_enrollment_expiry_default(app_request):
    assert session.enrollment_expiry(app_request) is None


@pytest.mark.django_db
def test_enrollment_expiry_not_datetime(app_request):
    session.update(app_request, enrollment_expiry="2024-03-25T00:00:00Z")

    assert session.enrollment_expiry(app_request) is None


@pytest.mark.django_db
def test_enrollment_expiry_datetime_timezone_utc(app_request):
    expiry = datetime.now(tz=timezone.utc)

    session.update(app_request, enrollment_expiry=expiry)

    assert session.enrollment_expiry(app_request) == expiry


@pytest.mark.django_db
def test_enrollment_expiry_datetime_timezone_naive(app_request):
    expiry = datetime.now()
    assert expiry.tzinfo is None

    session.update(app_request, enrollment_expiry=expiry)
    session_expiry = session.enrollment_expiry(app_request)

    assert all(
        [
            session_expiry.year == expiry.year,
            session_expiry.month == expiry.month,
            session_expiry.day == expiry.day,
            session_expiry.hour == expiry.hour,
            session_expiry.minute == expiry.minute,
            session_expiry.second == expiry.second,
            session_expiry.tzinfo == timezone.utc,
        ]
    )


@pytest.mark.django_db
def test_enrollment_token_default(app_request):
    assert session.enrollment_token(app_request) is None
    assert session.enrollment_token_expiry(app_request) is None


@pytest.mark.django_db
def test_enrollment_token_valid_expired(app_request):
    # valid token expired in the far past
    token = "token"
    exp = time.time() - 10000

    session.update(app_request, enrollment_token=token, enrollment_token_exp=exp)

    assert not session.enrollment_token_valid(app_request)


@pytest.mark.django_db
def test_enrollment_token_valid_invalid(app_request):
    # invalid token expiring in the far future
    token = None
    exp = time.time() + 10000

    session.update(app_request, enrollment_token=token, enrollment_token_exp=exp)

    assert not session.enrollment_token_valid(app_request)


@pytest.mark.django_db
def test_enrollment_token_valid_valid(app_request):
    # valid token expiring in the far future
    token = "token"
    exp = time.time() + 10000

    session.update(app_request, enrollment_token=token, enrollment_token_exp=exp)

    assert session.enrollment_token_valid(app_request)


@pytest.mark.django_db
def test_language_default(app_request):
    assert session.language(app_request) == "en"


@pytest.mark.django_db
def test_language_es(app_request):
    app_request.LANGUAGE_CODE = "es"
    assert session.language(app_request) == "es"


@pytest.mark.django_db
def test_logged_in_default(app_request):
    assert not session.logged_in(app_request)


@pytest.mark.django_db
def test_logged_in_False(app_request):
    session.update(app_request, oauth_token=False)

    assert not session.logged_in(app_request)


@pytest.mark.django_db
def test_logged_in_True(app_request):
    session.update(app_request, oauth_token=True)

    assert session.logged_in(app_request)


@pytest.mark.django_db
def test_logout(app_request):
    session.update(app_request, oauth_claim="oauth_claim", oauth_token="oauth_token", enrollment_token="enrollment_token")
    assert session.logged_in(app_request)
    assert session.oauth_claim(app_request)

    session.logout(app_request)

    assert not session.logged_in(app_request)
    assert not session.enrollment_token(app_request)
    assert not session.oauth_token(app_request)
    assert not session.oauth_claim(app_request)


@pytest.mark.django_db
def test_oauth_token_default(app_request):
    assert not session.oauth_token(app_request)


@pytest.mark.django_db
def test_origin_default(rf):
    # create a new request without initializing the app's session
    app_request = rf.get("/some/path")
    assert not hasattr(app_request, "session")

    SessionMiddleware(lambda x: x).process_request(app_request)

    assert hasattr(app_request, "session")
    app_request.session.save()

    assert session._ORIGIN not in app_request.session
    assert session.origin(app_request) == reverse(ROUTE_INDEX)


@pytest.mark.django_db
def test_reset_agency(model_TransitAgency, app_request):
    session.update(app_request, agency=model_TransitAgency)

    assert session.agency(app_request)

    session.reset(app_request)

    assert session.agency(app_request) is None


@pytest.mark.django_db
def test_reset_eligibility(app_request):
    app_request.session[session._ELIGIBILITY] = ["type1"]

    session.reset(app_request)

    assert session.eligibility(app_request) is None


@pytest.mark.django_db
def test_reset_enrollment(app_request):
    app_request.session[session._ENROLLMENT_TOKEN] = "enrollmenttoken123"
    app_request.session[session._ENROLLMENT_TOKEN_EXP] = "1234567890"

    session.reset(app_request)

    assert session.enrollment_token(app_request) is None
    assert session.enrollment_token_expiry(app_request) is None
    assert not session.enrollment_token_valid(app_request)


@pytest.mark.django_db
def test_reset_oauth(app_request):
    app_request.session[session._OAUTH_TOKEN] = "oauthtoken456"
    app_request.session[session._OAUTH_CLAIM] = "claim"

    session.reset(app_request)

    assert session.oauth_token(app_request) is None
    assert session.oauth_claim(app_request) is None


@pytest.mark.django_db
def test_reset_origin(app_request):
    app_request.session[session._ORIGIN] = "/origin"

    session.reset(app_request)

    assert session.origin(app_request) == reverse(ROUTE_INDEX)


@pytest.mark.django_db
def test_reset_start(app_request):
    # start shouldn't change between resets
    start = session.start(app_request)

    session.reset(app_request)

    assert session.start(app_request) == start


@pytest.mark.django_db
def test_reset_verifier(app_request):
    app_request.session[session._VERIFIER] = "verifier"

    session.reset(app_request)

    assert session.verifier(app_request) is None


@pytest.mark.django_db
def test_reset_user(app_request):
    # subsequent reset should not overwrite these
    uid = session.uid(app_request)
    did = session.did(app_request)

    assert uid
    assert did

    session.reset(app_request)

    assert session.uid(app_request) == uid
    assert session.did(app_request) == did


@pytest.mark.django_db
def test_start_default(app_request, mocker):
    # start() resets and returns a value when user is not configured
    spy = mocker.spy(session, "reset")
    app_request.session[session._START] = None
    app_request.session[session._UID] = None

    t0 = time.time()
    start = session.start(app_request)

    spy.assert_called_once()
    assert isinstance(start, int)
    assert start >= t0


@pytest.mark.django_db
def test_uid_default(app_request, mocker):
    # uid() resets and returns a value when user is not configured
    spy = mocker.spy(session, "reset")
    app_request.session[session._UID] = None

    uid = session.uid(app_request)

    spy.assert_called_once()
    assert uid
    assert isinstance(uid, str)
    assert uid != "None"


@pytest.mark.django_db
def test_update_agency_None(app_request):
    session.update(app_request, agency=None)

    assert session.agency(app_request) is None


@pytest.mark.django_db
def test_update_agency_str(app_request):
    session.update(app_request, agency="abc")

    assert session.agency(app_request) is None


@pytest.mark.django_db
def test_update_agency_int(app_request):
    session.update(app_request, agency=1)

    assert session.agency(app_request) is None


@pytest.mark.django_db
def test_update_agency_TransitAgency(app_request):
    agency = models.TransitAgency.objects.first()

    session.update(app_request, agency=agency)

    assert session.agency(app_request) == agency


@pytest.mark.django_db
def test_update_debug_None(app_request):
    debug = session.debug(app_request)
    session.update(app_request, debug=None)

    assert session.debug(app_request) == debug


@pytest.mark.django_db
def test_update_debug_False(app_request):
    session.update(app_request, debug=False)

    assert not session.debug(app_request)


@pytest.mark.django_db
def test_update_debug_True(app_request):
    session.update(app_request, debug=True)

    assert session.debug(app_request)


@pytest.mark.django_db
def test_update_eligibility_empty(app_request):
    session.update(app_request, eligibility_types=[])

    assert session.eligibility(app_request) is None


@pytest.mark.django_db
def test_update_eligibility_many(model_EligibilityType, app_request):
    with pytest.raises(NotImplementedError):
        assert session.update(app_request, eligibility_types=[model_EligibilityType, model_EligibilityType])


@pytest.mark.django_db
def test_update_eligibility_single(model_TransitAgency, app_request):
    eligibility = model_TransitAgency.eligibility_types.first()

    session.update(app_request, agency=model_TransitAgency, eligibility_types=[eligibility.name])

    assert session.eligibility(app_request) == eligibility


@pytest.mark.django_db
def test_update_enrollment_token(app_request):
    token = "token"
    exp = 1234567890

    session.update(app_request, enrollment_token=token, enrollment_token_exp=exp)

    assert session.enrollment_token(app_request) == token
    assert session.enrollment_token_expiry(app_request) == exp


@pytest.mark.django_db
def test_update_oauth_token(app_request):
    session.update(app_request, oauth_token="token")

    assert session.oauth_token(app_request) == "token"


@pytest.mark.django_db
def test_update_origin(app_request):
    session.update(app_request, origin="/origin")

    assert session.origin(app_request) == "/origin"


@pytest.mark.django_db
def test_update_verifier(app_request):
    verifier = models.EligibilityVerifier.objects.first()

    session.update(app_request, verifier=verifier)

    assert session.verifier(app_request) == verifier


@pytest.mark.django_db
def test_verifier_default(app_request):
    assert session.verifier(app_request) is None
