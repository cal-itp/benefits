import time

from django.urls import reverse
import pytest

from benefits.core import models, session


@pytest.mark.django_db
def test_active_agency_False(app_request):
    session.update(app_request, agency=None)

    assert not session.active_agency(app_request)

    agency = models.TransitAgency.objects.first()
    agency.active = False
    agency.save()

    session.update(app_request, agency=agency)

    assert not session.active_agency(app_request)


@pytest.mark.django_db
def test_active_agency_True(app_request):
    agency = models.TransitAgency.objects.filter(active=True).first()
    session.update(app_request, agency=agency)

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
def test_eligibile_True(app_request):
    agency = models.TransitAgency.objects.first()
    eligibility = agency.eligibility_types.first()

    session.update(app_request, agency=agency, eligibility_types=[eligibility.name])

    assert session.eligible(app_request)


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
    session.update(app_request, oauth_token="oauth_token", enrollment_token="enrollment_token")
    assert session.logged_in(app_request)

    session.logout(app_request)

    assert not session.logged_in(app_request)
    assert not session.enrollment_token(app_request)
    assert not session.oauth_token(app_request)


@pytest.mark.django_db
def test_oauth_token_default(app_request):
    assert not session.oauth_token(app_request)


@pytest.mark.django_db
def test_rate_limit_counter_default(app_request):
    assert session.rate_limit_counter(app_request) == 0


@pytest.mark.django_db
def test_rate_limit_counter_increment(app_request):
    session.reset_rate_limit(app_request)
    session.increment_rate_limit_counter(app_request)

    c1 = session.rate_limit_counter(app_request)
    assert isinstance(c1, int)
    assert c1 > 0

    session.increment_rate_limit_counter(app_request)

    c2 = session.rate_limit_counter(app_request)
    assert c2 == c1 + 1


@pytest.mark.django_db
def test_rate_limit_reset(mocker, app_request):
    mocker.patch.object(session.settings, "RATE_LIMIT_PERIOD", 100)
    t0 = int(time.time())

    session.reset_rate_limit(app_request)

    assert session.rate_limit_counter(app_request) == 0
    assert session.rate_limit_time(app_request) >= t0 + 100


@pytest.mark.django_db
def test_rate_limit_time_default(app_request):
    # a reset session also resets rate limit time (t0), which should have already happened coming into this test
    t0 = session.rate_limit_time(app_request)
    t1 = int(time.time())

    assert t1 >= t0


@pytest.mark.django_db
def test_reset_agency(app_request):
    agency = models.TransitAgency.objects.first()
    session.update(app_request, agency=agency)

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

    session.reset(app_request)

    assert session.oauth_token(app_request) is None


@pytest.mark.django_db
def test_reset_origin(app_request):
    app_request.session[session._ORIGIN] = "/origin"

    session.reset(app_request)

    assert session.origin(app_request) == reverse("core:index")


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
def test_update_eligibility_many(app_request):
    eligiblity = models.EligibilityType.objects.all()

    with pytest.raises(NotImplementedError):
        assert session.update(app_request, eligibility_types=[e.name for e in eligiblity])


@pytest.mark.django_db
def test_update_eligibility_single(app_request):
    agency = models.TransitAgency.objects.first()
    eligibility = agency.eligibility_types.first()

    session.update(app_request, agency=agency, eligibility_types=[eligibility.name])

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
