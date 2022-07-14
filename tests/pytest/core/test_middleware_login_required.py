from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

import pytest

from benefits.core import session
from benefits.core.middleware import LoginRequired
from benefits.core.models import EligibilityVerifier

ROUTE_LOGIN = "oauth:login"


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(LoginRequired)(mocked_view)


@pytest.fixture
def require_login(mocker):
    mock_verifier = mocker.Mock(spec=EligibilityVerifier)
    mock_verifier.is_auth_required = True
    mocker.patch("benefits.core.session.verifier", return_value=mock_verifier)


@pytest.mark.django_db
@pytest.mark.usefixtures("require_login")
def test_login_auth_required(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()

    assert response.status_code == 302
    assert response.headers["Location"] == reverse(ROUTE_LOGIN)


@pytest.mark.django_db
@pytest.mark.usefixtures("model_EligibilityVerifier")
def test_login_auth_not_required(app_request, mocked_view, decorated_view):
    verifier = EligibilityVerifier.objects.filter(auth_provider__isnull=True).first()
    assert verifier
    assert not verifier.is_auth_required
    session.update(app_request, verifier=verifier)

    decorated_view(app_request)

    mocked_view.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("require_login")
def test_logged_in(app_request, mocked_view, decorated_view):
    # log in
    session.update(app_request, oauth_token="something")

    decorated_view(app_request)
    mocked_view.assert_called_once()
