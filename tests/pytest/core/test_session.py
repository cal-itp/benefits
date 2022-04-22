from django.urls import reverse
import pytest

from benefits.core import models, session


@pytest.mark.django_db
def test_agency(session_request):
    session.update(session_request, agency=None)
    assert session.agency(session_request) is None

    session.update(session_request, agency="abc")
    assert session.agency(session_request) is None

    session.update(session_request, agency=1)
    assert session.agency(session_request) is None

    agency = models.TransitAgency.objects.first()
    session.update(session_request, agency=agency)
    assert session.agency(session_request) == agency


@pytest.mark.django_db
def test_reset(session_request):
    # fill key session variables with fake data
    session_request.session[session._AGENCY] = "abc"
    session_request.session[session._ELIGIBILITY] = ["type1"]
    session_request.session[session._ENROLLMENT_TOKEN] = "enrollmenttoken123"
    session_request.session[session._ENROLLMENT_TOKEN_EXP] = "1234567890"
    session_request.session[session._OAUTH_TOKEN] = "oauthtoken456"
    session_request.session[session._ORIGIN] = "/origin"
    session_request.session[session._VERIFIER] = "verifier"

    session.reset(session_request)

    # see that they were cleared
    assert session.agency(session_request) is None
    assert session.did(session_request) is not None
    assert session.eligibility(session_request) is None
    assert session.enrollment_token(session_request) is None
    assert session.enrollment_token_expiry(session_request) is None
    assert session.oauth_token(session_request) is None
    assert session.origin(session_request) == reverse("core:index")
    assert session.uid(session_request) is not None
    assert session.verifier(session_request) is None

    # reset generated uid, did
    uid = session.uid(session_request)
    did = session.did(session_request)

    session.reset(session_request)

    # subsequent reset should not overwrite these
    assert session.uid(session_request) == uid
    assert session.did(session_request) == did
