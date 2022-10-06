from django.urls import reverse

import pytest


from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.eligibility.forms import EligibilityVerifierSelectionForm
from benefits.eligibility.views import (
    ROUTE_INDEX,
    ROUTE_START,
    ROUTE_LOGIN,
    ROUTE_CONFIRM,
    ROUTE_ENROLLMENT,
    TEMPLATE_INDEX,
    TEMPLATE_CONFIRM,
    TEMPLATE_UNVERIFIED,
)

import benefits.eligibility.views


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


@pytest.fixture
def mocked_verifier_form(mocker):
    mock_form = mocker.Mock(spec=EligibilityVerifierSelectionForm)
    mocker.patch("benefits.eligibility.views.forms.EligibilityVerifierSelectionForm", return_value=mock_form)


@pytest.fixture(autouse=True)
def disable_rate_limit(mocker):
    # override session rate limit handling for all tests
    mock_settings = mocker.patch("benefits.core.middleware.settings")
    mock_settings.RATE_LIMIT_ENABLED = False


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_get_agency_multiple_verifiers(
    mocker, model_TransitAgency, model_EligibilityVerifier, mocked_session_agency, client
):
    # override the mocked session agency with a mock agency that has multiple verifiers
    mock_agency = mocker.Mock(spec=model_TransitAgency)
    mock_agency.eligibility_verifiers.all.return_value = [model_EligibilityVerifier, model_EligibilityVerifier]
    mock_agency.eligibility_verifiers.count.return_value = 2
    mocked_session_agency.return_value = mock_agency

    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_INDEX
    assert "page" in response.context_data
    assert len(response.context_data["page"].forms) > 0
    assert isinstance(response.context_data["page"].forms[0], EligibilityVerifierSelectionForm)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_get_agency_single_verifier(
    mocker, model_TransitAgency, model_EligibilityVerifier, mocked_session_agency, client
):
    # override the mocked session agency with a mock agency that has a single verifier
    mock_agency = mocker.Mock(spec=model_TransitAgency)
    mock_agency.eligibility_verifiers.all.return_value = [model_EligibilityVerifier]
    mock_agency.eligibility_verifiers.count.return_value = 1
    mocked_session_agency.return_value = mock_agency

    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_START)


@pytest.mark.django_db
def test_index_get_without_agency(client):
    path = reverse(ROUTE_INDEX)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_post_invalid_form(client):
    path = reverse(ROUTE_INDEX)

    response = client.post(path, {"invalid": "data"})

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_INDEX


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_post_valid_form(client, model_EligibilityVerifier, mocked_session_update):
    path = reverse(ROUTE_INDEX)

    response = client.post(path, {"verifier": model_EligibilityVerifier.id})

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_START)
    assert mocked_session_update.call_args.kwargs["verifier"] == model_EligibilityVerifier


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_verifier_form", "mocked_session_verifier_auth_required")
def test_start_verifier_auth_required_logged_in(mocker, client):
    mock_session = mocker.patch("benefits.eligibility.views.session")
    mock_session.logged_in.return_value = True

    path = reverse(ROUTE_START)
    response = client.get(path)

    assert response.status_code == 200
    assert "page" in response.context_data
    assert len(response.context_data["page"].buttons) == 1
    assert response.context_data["page"].buttons[0].url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_verifier_form", "mocked_session_verifier_auth_required")
def test_start_verifier_auth_required_not_logged_in(mocker, client):
    mock_session = mocker.patch("benefits.eligibility.views.session")
    mock_session.logged_in.return_value = False

    path = reverse(ROUTE_START)
    response = client.get(path)

    assert response.status_code == 200
    assert "page" in response.context_data
    assert len(response.context_data["page"].buttons) == 1
    assert response.context_data["page"].buttons[0].url == reverse(ROUTE_LOGIN)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_verifier_form", "mocked_session_verifier_auth_not_required")
def test_start_verifier_auth_not_required(client):
    path = reverse(ROUTE_START)
    response = client.get(path)

    assert response.status_code == 200
    assert "page" in response.context_data
    assert len(response.context_data["page"].buttons) == 1
    assert response.context_data["page"].buttons[0].url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_start_without_verifier(client):
    path = reverse(ROUTE_START)

    response = client.get(path)
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier_auth_not_required")
def test_confirm_get_unverified(mocker, client):
    mock_page = mocker.patch("benefits.eligibility.views.viewmodels.Page")
    mock_page.return_value.context_dict.return_value = {"page": {"title": "page title", "headline": "page headline"}}

    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility", "mocked_session_verifier_auth_not_required")
def test_confirm_get_verified(client, mocked_session_update):
    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)
    mocked_session_update.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier_oauth", "mocked_session_oauth_token")
def test_confirm_get_oauth_verified(mocker, client, model_EligibilityType, mocked_session_update, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_oauth", return_value=[model_EligibilityType])

    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_verifier_oauth", "mocked_session_oauth_token", "mocked_session_update"
)
def test_confirm_get_oauth_unverified(mocker, client, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_oauth", return_value=[])

    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    mocked_analytics_module.returned_fail.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_UNVERIFIED


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
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=None)

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, form_data)

    mocked_analytics_module.returned_error.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_valid_form_eligibility_unverified(mocker, client, form_data, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=[])

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
    eligibility = mocked_session_eligibility.return_value
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=[eligibility])

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, form_data)

    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)
