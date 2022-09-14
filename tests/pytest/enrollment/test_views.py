import time

from django.urls import reverse

import pytest

from benefits.enrollment.views import (
    ROUTE_INDEX,
    ROUTE_TOKEN,
    ROUTE_SUCCESS,
    ROUTE_RETRY,
    TEMPLATE_INDEX,
    TEMPLATE_SUCCESS,
    TEMPLATE_RETRY,
)

import benefits.enrollment.views


@pytest.fixture
def card_tokenize_form_data():
    return {"card_token": "tokenized_card"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment.views)


@pytest.mark.django_db
def test_token_ineligible(client):
    path = reverse(ROUTE_TOKEN)
    with pytest.raises(AttributeError, match=r"eligibility"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_token_refresh(mocker, client):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=False)

    mock_client = mocker.patch("benefits.enrollment.views.api.Client.access_token")
    mock_token = mocker.Mock()
    mock_token.access_token = "access_token"
    mock_token.expiry = time.time() + 10000
    mock_client.return_value = mock_token

    path = reverse(ROUTE_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == mock_token.access_token


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_token_valid(mocker, client):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=True)
    mocker.patch("benefits.core.session.enrollment_token", return_value="enrollment_token")

    path = reverse(ROUTE_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == "enrollment_token"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible_get(client):
    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_INDEX
    assert "page" in response.context_data
    assert "payment_processor" in response.context_data
    assert "forms" in response.context_data
    assert "tokenize_retry" in response.context_data["forms"]
    assert "tokenize_success" in response.context_data["forms"]


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible_post_invalid_form(client, invalid_form_data):
    path = reverse(ROUTE_INDEX)

    with pytest.raises(Exception, match=r"form"):
        client.post(path, invalid_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_failure(mocker, client, card_tokenize_form_data):
    mock_response = mocker.Mock()
    mock_response.success = False
    mock_response.message = "Mock error message"
    mocker.patch("benefits.enrollment.views.api.Client.enroll", return_value=mock_response)

    path = reverse(ROUTE_INDEX)
    with pytest.raises(Exception, match=mock_response.message):
        client.post(path, card_tokenize_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success(
    mocker, client, card_tokenize_form_data, mocked_analytics_module, model_EligibilityType
):
    mock_response = mocker.Mock()
    mock_response.success = True
    mocker.patch("benefits.enrollment.views.api.Client.enroll", return_value=mock_response)

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    mocked_analytics_module.returned_success.assert_called_once()
    assert model_EligibilityType.group_id in mocked_analytics_module.returned_success.call_args.args


@pytest.mark.django_db
def test_index_ineligible(client):
    path = reverse(ROUTE_INDEX)
    with pytest.raises(AttributeError, match=r"eligibility"):
        client.get(path)


@pytest.mark.django_db
def test_retry_ineligible(client):
    path = reverse(ROUTE_RETRY)
    with pytest.raises(AttributeError, match=r"eligibility"):
        client.post(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_eligibility")
def test_retry_get(client):
    path = reverse(ROUTE_RETRY)
    with pytest.raises(Exception, match=r"POST"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_eligibility")
def test_retry_invalid_form(mocker, client):
    mocker.patch("benefits.enrollment.views.forms.CardTokenizeFailForm.is_valid", return_value=False)

    path = reverse(ROUTE_RETRY)
    with pytest.raises(Exception, match=r"Invalid"):
        client.post(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_retry_valid_form(mocker, client, mocked_analytics_module):
    mocker.patch("benefits.enrollment.views.forms.CardTokenizeFailForm.is_valid", return_value=True)

    path = reverse(ROUTE_RETRY)
    response = client.post(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_RETRY
    mocked_analytics_module.returned_retry.assert_called_once()


@pytest.mark.django_db
def test_success_no_verifier(client):
    path = reverse(ROUTE_SUCCESS)
    with pytest.raises(AttributeError, match=r"verifier"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_success_authentication_logged_in(mocker, client):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = True

    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    assert "page" in response.context_data
    assert "logged-in" in response.context_data["page"].classes


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_success_authentication_not_logged_in(mocker, client):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = False

    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    assert "page" in response.context_data
    assert "logged-out" in response.context_data["page"].classes


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_not_required")
def test_success_no_authentication(client):
    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    assert "page" in response.context_data
    assert "logged-in" not in response.context_data["page"].classes
