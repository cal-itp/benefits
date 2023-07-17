from django.utils.decorators import decorator_from_middleware

import pytest

from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.oauth.middleware import VerifierUsesAuthVerificationSessionRequired


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(VerifierUsesAuthVerificationSessionRequired)(mocked_view)


@pytest.mark.django_db
def test_authverifier_required_no_verifier(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_not_required")
def test_authverifier_required_no_authverifier(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_oauth")
def test_authverifier_required_authverifier(app_request, mocked_view, decorated_view):
    decorated_view(app_request)

    mocked_view.assert_called_once()
