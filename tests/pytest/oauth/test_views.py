from django.http import HttpResponse
from django.urls import reverse

import pytest

from benefits.routes import routes
from benefits.core import session
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.oauth.views import (
    TEMPLATE_SYSTEM_ERROR,
    _oauth_client_or_error_redirect,
    system_error,
)
import benefits.oauth.views
import benefits.oauth.hooks


@pytest.fixture
def mocked_view_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.views)


@pytest.fixture
def mocked_hook_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.hooks)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.views, "sentry_sdk")


@pytest.fixture
def mocked_hook_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.hooks, "sentry_sdk")


@pytest.fixture
def mocked_oauth_client_or_error_redirect__client(mocked_oauth_create_client):
    mocked_oauth_create_client.return_value.authorize_redirect.return_value = HttpResponse("authorize redirect")
    mocked_oauth_create_client.return_value.authorize_access_token.return_value = HttpResponse("authorize access token")
    mocked_oauth_create_client.return_value.load_server_metadata.return_value = HttpResponse("load server metadata")
    return mocked_oauth_create_client


@pytest.fixture
def mocked_oauth_client_or_error_redirect__error(mocked_oauth_create_client):
    mocked_oauth_create_client.side_effect = Exception("Side effect")
    return mocked_oauth_create_client


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_oauth_client_or_error_redirect_no_oauth_client(
    app_request,
    model_EnrollmentFlow_with_scope_and_claim,
    mocked_oauth_create_client,
    mocked_view_analytics_module,
    mocked_sentry_sdk_module,
):
    mocked_oauth_create_client.return_value = None

    result = _oauth_client_or_error_redirect(app_request, model_EnrollmentFlow_with_scope_and_claim)

    assert result.status_code == 302
    assert result.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_view_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_oauth_client_or_error_redirect__error")
def test_oauth_client_or_error_redirect_oauth_client_exception(
    app_request, model_EnrollmentFlow_with_scope_and_claim, mocked_view_analytics_module, mocked_sentry_sdk_module
):
    result = _oauth_client_or_error_redirect(app_request, model_EnrollmentFlow_with_scope_and_claim)

    assert result.status_code == 302
    assert result.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_view_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_oauth_create_client")
def test_oauth_client_or_error_oauth_client(
    app_request, model_EnrollmentFlow_with_scope_and_claim, mocked_view_analytics_module, mocked_sentry_sdk_module
):
    result = _oauth_client_or_error_redirect(app_request, model_EnrollmentFlow_with_scope_and_claim)

    assert hasattr(result, "authorize_redirect")
    mocked_view_analytics_module.error.assert_not_called()
    mocked_sentry_sdk_module.capture_exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_oauth_client_or_error_redirect__error")
def test_login_oauth_client_init_error(client, mocked_hook_analytics_module, mocked_hook_sentry_sdk_module):
    path = reverse(routes.OAUTH_LOGIN)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_hook_analytics_module.error.assert_called_once()
    mocked_hook_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "route",
    [routes.OAUTH_LOGIN, routes.OAUTH_AUTHORIZE, routes.OAUTH_CANCEL, routes.OAUTH_LOGOUT, routes.OAUTH_POST_LOGOUT],
)
def test_url_path_no_session_flow(client, route):
    path = reverse(route)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_authorize_oauth_client_init_error(client, mocked_hook_analytics_module, mocked_hook_sentry_sdk_module):
    path = reverse(routes.OAUTH_AUTHORIZE)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_hook_analytics_module.error.assert_called_once()
    mocked_hook_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_cancel(client, mocked_hook_analytics_module):
    unverified_route = reverse(routes.ELIGIBILITY_UNVERIFIED)

    path = reverse(routes.OAUTH_CANCEL)
    response = client.get(path)

    mocked_hook_analytics_module.canceled_sign_in.assert_called_once()
    assert response.status_code == 302
    assert response.url == unverified_route


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_post_logout(mocker, client, mocked_hook_analytics_module):
    origin = reverse(routes.INDEX)
    mocker.patch("benefits.oauth.hooks.session.origin", return_value=origin)

    path = reverse(routes.OAUTH_POST_LOGOUT)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == origin
    mocked_hook_analytics_module.finished_sign_out.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_system_error(app_request, model_TransitAgency):
    origin = reverse(routes.ELIGIBILITY_START)
    session.update(app_request, origin=origin)

    result = system_error(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_SYSTEM_ERROR
    assert session.origin(app_request) == model_TransitAgency.index_url


@pytest.mark.django_db
def test_system_error_no_agency(app_request):
    result = system_error(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR
