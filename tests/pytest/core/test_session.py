from django.urls import reverse
import pytest

from benefits.core import models, session


@pytest.mark.django_db
def test_active_agency_False(session_request):
    session.update(session_request, agency=None)

    assert not session.active_agency(session_request)


@pytest.mark.django_db
def test_active_agency_True(session_request):
    agency = models.TransitAgency.objects.filter(active=True).first()
    session.update(session_request, agency=agency)

    assert session.active_agency(session_request)


@pytest.mark.django_db
def test_debug_default(session_request):
    assert session._DEBUG not in session_request.session
    assert not session.debug(session_request)


@pytest.mark.django_db
def test_debug_False(session_request):
    session.update(session_request, debug=False)

    assert not session.debug(session_request)


@pytest.mark.django_db
def test_debug_True(session_request):
    session.update(session_request, debug=True)

    assert session.debug(session_request)


@pytest.mark.django_db
def test_reset_agency(session_request):
    session_request.session[session._AGENCY] = "abc"

    session.reset(session_request)

    assert session.agency(session_request) is None
    assert not session.active_agency(session_request)


@pytest.mark.django_db
def test_reset_eligibility(session_request):
    session_request.session[session._ELIGIBILITY] = ["type1"]

    session.reset(session_request)

    assert session.eligibility(session_request) is None


@pytest.mark.django_db
def test_reset_enrollment(session_request):
    session_request.session[session._ENROLLMENT_TOKEN] = "enrollmenttoken123"
    session_request.session[session._ENROLLMENT_TOKEN_EXP] = "1234567890"

    session.reset(session_request)

    assert session.enrollment_token(session_request) is None
    assert session.enrollment_token_expiry(session_request) is None
    assert not session.valid_enrollment_token(session_request)


@pytest.mark.django_db
def test_reset_oauth(session_request):
    session_request.session[session._OAUTH_TOKEN] = "oauthtoken456"
    session_request.session[session._ORIGIN] = "/origin"

    session.reset(session_request)

    assert session.oauth_token(session_request) is None


@pytest.mark.django_db
def test_reset_origin(session_request):
    session_request.session[session._ORIGIN] = "/origin"
    assert session.origin(session_request) == "/origin"

    session.reset(session_request)

    assert session.origin(session_request) == reverse("core:index")


@pytest.mark.django_db
def test_reset_verifier(session_request):
    session_request.session[session._VERIFIER] = "verifier"

    session.reset(session_request)

    assert session.verifier(session_request) is None


@pytest.mark.django_db
def test_reset_user(session_request):
    session.reset(session_request)

    assert session.did(session_request) is not None
    assert session.uid(session_request) is not None

    # subsequent reset should not overwrite these
    uid = session.uid(session_request)
    did = session.did(session_request)

    session.reset(session_request)

    assert session.uid(session_request) == uid
    assert session.did(session_request) == did


@pytest.mark.django_db
def test_update_agency_None(session_request):
    session.update(session_request, agency=None)

    assert session.agency(session_request) is None


@pytest.mark.django_db
def test_update_agency_str(session_request):
    session.update(session_request, agency="abc")

    assert session.agency(session_request) is None


@pytest.mark.django_db
def test_update_agency_int(session_request):
    session.update(session_request, agency=1)

    assert session.agency(session_request) is None


@pytest.mark.django_db
def test_update_agency_TransitAgency(session_request):
    agency = models.TransitAgency.objects.first()

    session.update(session_request, agency=agency)

    assert session.agency(session_request) == agency
