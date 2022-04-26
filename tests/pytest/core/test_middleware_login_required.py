from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

import pytest

from benefits.core import session
from benefits.core.middleware import LoginRequired
from benefits.core.models import EligibilityVerifier

login_path = reverse("oauth:login")


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(LoginRequired)(mocked_view)


def require_login(request):
    verifier = EligibilityVerifier.objects.filter(auth_provider__isnull=False).first()
    assert verifier
    assert verifier.requires_authentication
    session.update(request, verifier=verifier)


@pytest.mark.django_db
def test_login_auth_required(app_request, mocked_view, decorated_view):
    require_login(app_request)
    response = decorated_view(app_request)

    mocked_view.assert_not_called()

    assert response.status_code == 302
    assert response.headers["Location"] == login_path


@pytest.mark.django_db
def test_login_auth_not_required(app_request, mocked_view, decorated_view):
    verifier = EligibilityVerifier.objects.filter(auth_provider__isnull=True).first()
    assert verifier
    assert not verifier.requires_authentication
    session.update(app_request, verifier=verifier)

    decorated_view(app_request)

    mocked_view.assert_called_once()


@pytest.mark.django_db
def test_logged_in(app_request, mocked_view, decorated_view):
    require_login(app_request)

    # log in
    session.update(app_request, oauth_token="something")

    decorated_view(app_request)
    mocked_view.assert_called_once()
