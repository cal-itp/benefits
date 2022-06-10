from django.urls import reverse

import pytest

from benefits.core import session
from benefits.eligibility.views import confirm
import benefits.eligibility.views


ROUTE_INDEX = "eligibility:index"
ROUTE_START = "eligibility:start"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_ENROLLMENT = "enrollment:index"
TEMPLATE_CONFIRM = "eligibility/confirm.html"
TEMPLATE_UNVERIFIED = "eligibility/unverified.html"


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.eligibility.views)


@pytest.fixture
def mocked_oauth_token_request(mocker, app_request):
    mocker.patch("benefits.core.session.oauth_token", autospec=True, return_value="token")
    assert session.logged_in(app_request)
    return app_request


@pytest.fixture
def mocked_confirm_request_invalid_form(mocked_oauth_token_request):
    mocked_oauth_token_request.method = "POST"
    return mocked_oauth_token_request


@pytest.fixture
def mocked_confirm_request_valid_form(mocked_confirm_request_invalid_form):
    mocked_confirm_request_invalid_form.POST = {"sub": "A1234567", "name": "Person"}
    return mocked_confirm_request_invalid_form


@pytest.fixture
def mocked_eligibile_request(mocked_oauth_token_request, mocked_session_eligibility):
    assert session.eligibility(mocked_oauth_token_request) == mocked_session_eligibility
    return mocked_oauth_token_request


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_with_agency(client):
    path = reverse(ROUTE_INDEX)
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_index_without_agency(client):
    path = reverse(ROUTE_INDEX)
    with pytest.raises(AttributeError, match=r"agency"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_start_with_verifier(client):
    path = reverse(ROUTE_START)
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_start_without_verifier(client):
    path = reverse(ROUTE_START)
    with pytest.raises(AttributeError, match=r"verifier"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_get_unverified(mocked_oauth_token_request):
    response = confirm(mocked_oauth_token_request)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_get_verified(mocked_eligibile_request, mocked_session_update):
    response = confirm(mocked_eligibile_request)

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)
    mocked_session_update.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_post_invalid_form(mocked_confirm_request_invalid_form, mocked_analytics_module):
    response = confirm(mocked_confirm_request_invalid_form)

    mocked_analytics_module.started_eligibility.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_post_recaptcha_fail(mocker, mocked_confirm_request_invalid_form, mocked_analytics_module):
    mocker.patch("benefits.eligibility.views.recaptcha.has_error", return_value=True)
    messages = mocker.spy(benefits.eligibility.views, "messages")

    confirm(mocked_confirm_request_invalid_form)

    messages.error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_post_valid_form_eligibility_error(mocker, mocked_confirm_request_valid_form, mocked_analytics_module):
    mocker.patch("benefits.eligibility.views.api.get_verified_types", return_value=None)

    response = confirm(mocked_confirm_request_valid_form)

    mocked_analytics_module.returned_error.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_post_valid_form_eligibility_unverified(mocker, mocked_confirm_request_valid_form, mocked_analytics_module):
    mocker.patch("benefits.eligibility.views.api.get_verified_types", return_value=[])

    response = confirm(mocked_confirm_request_valid_form)

    mocked_analytics_module.returned_fail.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_UNVERIFIED


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_post_valid_form_eligibility_verified(
    mocker, mocked_confirm_request_valid_form, mocked_session_eligibility, mocked_session_update, mocked_analytics_module
):
    mocker.patch("benefits.eligibility.views.api.get_verified_types", return_value=[mocked_session_eligibility])

    response = confirm(mocked_confirm_request_valid_form)

    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)
