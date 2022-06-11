from django.urls import reverse

import pytest

import benefits.eligibility.views
from benefits.eligibility.forms import EligibilityVerifierSelectionForm


ROUTE_INDEX = "eligibility:index"
ROUTE_START = "eligibility:start"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_ENROLLMENT = "enrollment:index"
TEMPLATE_CONFIRM = "eligibility/confirm.html"
TEMPLATE_UNVERIFIED = "eligibility/unverified.html"


@pytest.fixture
def form_data():
    return {"sub": "A1234567", "name": "Person"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.eligibility.views)


@pytest.fixture
def mocked_eligibility_auth_request(mocked_eligibility_request_session, mocked_session_oauth_token):
    """
    Stub fixture combines mocked_eligibility_request_session and mocked_session_oauth_token
    so that session behaves like in an authenticated request to the eligibility app
    """
    pass


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
@pytest.mark.usefixtures("mocked_eligibility_request_session")
def test_start_with_verifier(mocker, client):
    mock_form = mocker.Mock(spec=EligibilityVerifierSelectionForm)
    mocker.patch("benefits.eligibility.views.forms.EligibilityVerifierSelectionForm", return_value=mock_form)

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
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_get_unverified(client):
    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "mocked_session_eligibility")
def test_confirm_get_verified(client, mocked_session_update):
    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)
    mocked_session_update.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_invalid_form(client, invalid_form_data, mocked_analytics_module):
    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, invalid_form_data)

    mocked_analytics_module.started_eligibility.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module", "mocked_eligibility_auth_request")
def test_confirm_post_recaptcha_fail(mocker, client, invalid_form_data):
    mocker.patch("benefits.eligibility.views.recaptcha.has_error", return_value=True)
    messages = mocker.spy(benefits.eligibility.views, "messages")

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, invalid_form_data)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM
    messages.error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_valid_form_eligibility_error(mocker, client, form_data, mocked_analytics_module):
    mocker.patch("benefits.eligibility.views.api.get_verified_types", return_value=None)

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, form_data)

    mocked_analytics_module.returned_error.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_valid_form_eligibility_unverified(mocker, client, form_data, mocked_analytics_module):
    mocker.patch("benefits.eligibility.views.api.get_verified_types", return_value=[])

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, form_data)

    mocked_analytics_module.returned_fail.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_UNVERIFIED


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_valid_form_eligibility_verified(
    mocker, client, form_data, mocked_session_eligibility, mocked_session_update, mocked_analytics_module
):
    # mocked_session_eligibility is a fixture that mocks benefits.core.session.eligibility(request)
    # call it here, passing a None request, to get the return value from the mock
    eligibility = mocked_session_eligibility(None)
    mocker.patch("benefits.eligibility.views.api.get_verified_types", return_value=[eligibility])

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, form_data)

    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)
