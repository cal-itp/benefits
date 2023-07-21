from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

import pytest

from benefits.core import session
from benefits.core.middleware import LoginRequired

ROUTE_LOGIN = "oauth:login"


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(LoginRequired)(mocked_view)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_oauth")
def test_login_auth_required(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()

    assert response.status_code == 302
    assert response.headers["Location"] == reverse(ROUTE_LOGIN)


@pytest.mark.django_db
def test_login_auth_not_required(app_request, model_EligibilityVerifier, mocked_view, decorated_view):
    model_EligibilityVerifier.auth_provider = None
    assert not model_EligibilityVerifier.is_auth_required
    session.update(app_request, verifier=model_EligibilityVerifier)

    decorated_view(app_request)

    mocked_view.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_oauth")
def test_logged_in(app_request, mocked_view, decorated_view):
    # log in
    session.update(app_request, oauth_token="something")

    decorated_view(app_request)
    mocked_view.assert_called_once()
