import time

from benefits.enrollment_littlepay.session import Session


def test_access_token_default(app_request):
    session = Session(app_request)
    assert session.access_token is None
    assert session.access_token_expiry is None


def test_access_token_valid_expired(app_request):
    # valid token expired in the far past
    token = "token"
    exp = time.time() - 10000

    session = Session(app_request, access_token=token, access_token_expiry=exp)

    assert not session.access_token_valid()


def test_access_token_valid_invalid(app_request):
    # invalid token expiring in the far future
    token = None
    exp = time.time() + 10000

    session = Session(app_request, access_token=token, access_token_expiry=exp)

    assert not session.access_token_valid()


def test_access_token_valid_valid(app_request):
    # valid token expiring in the far future
    token = "token"
    exp = time.time() + 10000

    session = Session(app_request, access_token=token, access_token_expiry=exp)

    assert session.access_token_valid()
