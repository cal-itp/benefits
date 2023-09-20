from django.utils.decorators import decorator_from_middleware

import pytest

from benefits.core.middleware import VerifierSessionRequired, TEMPLATE_USER_ERROR


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(VerifierSessionRequired)(mocked_view)


@pytest.mark.django_db
def test_verifier_required_no_verifier(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_oauth")
def test_verifier_required_verifier(app_request, mocked_view, decorated_view):
    decorated_view(app_request)

    mocked_view.assert_called_once()
