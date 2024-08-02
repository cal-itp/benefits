from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

import pytest

from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.oauth.middleware import VerifierUsesAuthVerificationSessionRequired
import benefits.oauth.middleware
from benefits.oauth.redirects import ROUTE_SYSTEM_ERROR


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(VerifierUsesAuthVerificationSessionRequired)(mocked_view)


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.middleware)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.middleware, "sentry_sdk")


@pytest.mark.django_db
def test_authverifier_required_no_verifier(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_does_not_use_claims_verification")
def test_authverifier_required_no_authverifier(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.parametrize(("api_url", "form_class"), [(None, None), (None, ""), ("", None), ("", "")])
def test_authverifier_required_misconfigured_verifier(
    app_request,
    mocked_view,
    decorated_view,
    mocked_session_verifier_does_not_use_claims_verification,
    mocked_analytics_module,
    mocked_sentry_sdk_module,
    api_url,
    form_class,
):
    # fake a misconfigured verifier
    mocked_session_verifier_does_not_use_claims_verification.return_value.api_url = api_url
    mocked_session_verifier_does_not_use_claims_verification.return_value.form_class = form_class

    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(ROUTE_SYSTEM_ERROR)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_oauth")
def test_authverifier_required_authverifier(app_request, mocked_view, decorated_view):
    decorated_view(app_request)

    mocked_view.assert_called_once()
