from unittest.mock import create_autospec

import pytest
from benefits.core import session
from benefits.core.middleware import LoginRequired
from benefits.core.models import EligibilityVerifier
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from tests.pytest.conftest import initialize_session

login_path = reverse("oauth:login")


def require_login(request):
    verifier = EligibilityVerifier.objects.filter(auth_provider__isnull=False).first()
    assert verifier
    assert verifier.requires_authentication
    session.update(request, verifier=verifier)


@pytest.mark.django_db
def test_login_auth_required(rf):
    @decorator_from_middleware(LoginRequired)
    def test_view(request):
        pass

    mock = create_autospec(test_view)

    blocked_path = "/some/blocked/path"
    request = rf.get(blocked_path)
    initialize_session(request)
    require_login(request)

    response = test_view(request)

    mock.assert_not_called()

    assert response.status_code == 302
    assert response.headers["Location"] == login_path


@pytest.mark.django_db
def test_login_auth_not_required(rf):
    @decorator_from_middleware(LoginRequired)
    def test_view(request):
        pass

    mocked_view = create_autospec(test_view)

    blocked_path = "/some/blocked/path"
    request = rf.get(blocked_path)
    initialize_session(request)

    verifier = EligibilityVerifier.objects.filter(auth_provider__isnull=True).first()
    assert verifier
    assert not verifier.requires_authentication
    session.update(request, verifier=verifier)

    mocked_view(request)

    mocked_view.assert_called_once()


@pytest.mark.django_db
def test_logged_in(rf):
    @decorator_from_middleware(LoginRequired)
    def test_view(request):
        pass

    mocked_view = create_autospec(test_view)

    blocked_path = "/some/blocked/path"
    request = rf.get(blocked_path)
    initialize_session(request)
    require_login(request)

    # log in
    session.update(request, oauth_token="something")

    mocked_view(request)
    mocked_view.assert_called_once()


@pytest.mark.django_db
def test_login_restricted(client):
    test_page = reverse("oauth:test")
    response = client.get(test_page)
    assert response.status_code == 302
    assert response.headers["Location"] == login_path
