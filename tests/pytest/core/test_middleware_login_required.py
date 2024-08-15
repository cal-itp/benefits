from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

import pytest

from benefits.routes import routes
from benefits.core import session
from benefits.core.middleware import LoginRequired


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(LoginRequired)(mocked_view)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_login_flow_uses_claims_verification(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()

    assert response.status_code == 302
    assert response.headers["Location"] == reverse(routes.OAUTH_LOGIN)


@pytest.mark.django_db
def test_login_flow_does_not_use_claims_verification(app_request, model_EnrollmentFlow, mocked_view, decorated_view):
    model_EnrollmentFlow.claims_provider = None
    assert not model_EnrollmentFlow.uses_claims_verification
    session.update(app_request, flow=model_EnrollmentFlow)

    decorated_view(app_request)

    mocked_view.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_logged_in(app_request, mocked_view, decorated_view):
    # log in
    session.update(app_request, oauth_token="something")

    decorated_view(app_request)
    mocked_view.assert_called_once()
