from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

import pytest
from unittest.mock import create_autospec

from benefits.core import session
from benefits.core.middleware import LoginRequired
from benefits.core.models import EligibilityVerifier

from tests.pytest.conftest import initialize_request

login_path = reverse("oauth:login")


@pytest.fixture
def mocked_view():
    def test_view(request):
        pass

    return create_autospec(test_view)


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(LoginRequired)(mocked_view)


def require_login(request):
    verifier = EligibilityVerifier.objects.filter(auth_provider__isnull=False).first()
    assert verifier
    assert verifier.requires_authentication
    session.update(request, verifier=verifier)


@pytest.mark.django_db
def test_login_auth_required(rf, mocked_view, decorated_view):
    blocked_path = "/some/blocked/path"
    request = rf.get(blocked_path)
    initialize_request(request)
    require_login(request)

    response = decorated_view(request)

    mocked_view.assert_not_called()

    assert response.status_code == 302
    assert response.headers["Location"] == login_path


@pytest.mark.django_db
def test_login_auth_not_required(rf, mocked_view, decorated_view):
    blocked_path = "/some/blocked/path"
    request = rf.get(blocked_path)
    initialize_request(request)

    verifier = EligibilityVerifier.objects.filter(auth_provider__isnull=True).first()
    assert verifier
    assert not verifier.requires_authentication
    session.update(request, verifier=verifier)

    decorated_view(request)

    mocked_view.assert_called_once()


@pytest.mark.django_db
def test_logged_in(rf, mocked_view, decorated_view):
    blocked_path = "/some/blocked/path"
    request = rf.get(blocked_path)
    initialize_request(request)
    require_login(request)

    # log in
    session.update(request, oauth_token="something")

    decorated_view(request)
    mocked_view.assert_called_once()
