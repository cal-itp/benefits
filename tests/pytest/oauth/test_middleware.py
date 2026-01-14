import pytest
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

import benefits.oauth.middleware
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.oauth.middleware import FlowUsesClaimsVerificationSessionRequired
from benefits.routes import routes


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)(mocked_view)


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.middleware)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.middleware, "sentry_sdk")


@pytest.mark.django_db
def test_flow_using_claims_verification_required__no_flow(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_does_not_use_claims_verification")
def test_flow_using_claims_verification_required__no_identitygatewayconfig(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
def test_flow_using_claims_verification_required__misconfigured_flow(
    app_request,
    mocked_view,
    decorated_view,
    mocked_session_flow_does_not_use_claims_verification,
    mocked_analytics_module,
    mocked_sentry_sdk_module,
):
    # fake a misconfigured flow
    mocked_session_flow_does_not_use_claims_verification.return_value.api_request = None

    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(routes.OAUTH_SYSTEM_ERROR)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_flow_using_claims_verification_required__configured(app_request, mocked_view, decorated_view):
    decorated_view(app_request)

    mocked_view.assert_called_once()
