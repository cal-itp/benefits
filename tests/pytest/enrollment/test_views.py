import time

import pytest
from django.urls import reverse
from littlepay.api.funding_sources import FundingSourceResponse
from requests import HTTPError

import benefits.enrollment.views
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.views import ROUTE_LOGGED_OUT
from benefits.enrollment.views import (
    ROUTE_INDEX,
    ROUTE_REENROLLMENT_ERROR,
    ROUTE_RETRY,
    ROUTE_SUCCESS,
    ROUTE_TOKEN,
    TEMPLATE_SYSTEM_ERROR,
    TEMPLATE_RETRY,
)


@pytest.fixture
def card_tokenize_form_data():
    return {"card_token": "tokenized_card"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment.views, "sentry_sdk")


@pytest.fixture
def mocked_funding_source():
    return FundingSourceResponse(
        id="0",
        card_first_digits="0000",
        card_last_digits="0000",
        card_expiry_month="12",
        card_expiry_year="2024",
        card_scheme="visa",
        form_factor="physical",
        participant_id="cst",
        is_fpan=False,
        related_funding_sources=[],
    )


@pytest.mark.django_db
def test_token_ineligible(client):
    path = reverse(ROUTE_TOKEN)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_token_refresh(mocker, client):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=False)

    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_token = {}
    mock_token["access_token"] = "access_token"
    mock_token["expires_at"] = time.time() + 10000
    mock_client.request_card_tokenization_access.return_value = mock_token

    path = reverse(ROUTE_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == mock_token["access_token"]
    mock_client.oauth.ensure_active_token.assert_called_once()


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
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_get(client, model_EligibilityType):
    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EligibilityType.enrollment_index_template
    assert "forms" in response.context_data
    assert "cta_button" in response.context_data
    assert "card_tokenize_env" in response.context_data
    assert "card_tokenize_func" in response.context_data
    assert "card_tokenize_url" in response.context_data
    assert "token_field" in response.context_data
    assert "form_retry" in response.context_data
    assert "form_success" in response.context_data


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible_post_invalid_form(client, invalid_form_data):
    path = reverse(ROUTE_INDEX)

    with pytest.raises(Exception, match=r"form"):
        client.post(path, invalid_form_data)


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_http_error_500(
    mocker, client, mocked_analytics_module, mocked_sentry_sdk_module, card_tokenize_form_data, status_code
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error
    mock_client.link_concession_group_funding_source.side_effect = HTTPError(
        response=mock_error_response,
    )

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SYSTEM_ERROR
    mocked_analytics_module.returned_error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_http_error_400(mocker, client, card_tokenize_form_data):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value

    # any 400 level status_code that isn't 409 is considered an error
    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    mock_client.link_concession_group_funding_source.side_effect = HTTPError(
        response=mock_error_response,
    )

    path = reverse(ROUTE_INDEX)
    with pytest.raises(Exception, match=mock_error["message"]):
        client.post(path, card_tokenize_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_failure(mocker, client, card_tokenize_form_data):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value

    mock_client.link_concession_group_funding_source.side_effect = Exception("some other exception")

    path = reverse(ROUTE_INDEX)
    with pytest.raises(Exception, match=r"some other exception"):
        client.post(path, card_tokenize_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_customer_already_enrolled(
    mocker, client, card_tokenize_form_data, mocked_analytics_module, model_EligibilityType, mocked_funding_source
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source
    mock_error_response = mocker.Mock(status_code=409)
    mock_client.link_concession_group_funding_source.side_effect = HTTPError(response=mock_error_response)

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id, group_id=model_EligibilityType.group_id
    )
    assert response.status_code == 200
    assert response.template_name == model_EligibilityType.enrollment_success_template
    mocked_analytics_module.returned_success.assert_called_once()
    assert model_EligibilityType.group_id in mocked_analytics_module.returned_success.call_args.args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success(
    mocker, client, card_tokenize_form_data, mocked_analytics_module, model_EligibilityType, mocked_funding_source
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id, group_id=model_EligibilityType.group_id
    )
    assert response.status_code == 200
    assert response.template_name == model_EligibilityType.enrollment_success_template
    mocked_analytics_module.returned_success.assert_called_once()
    assert model_EligibilityType.group_id in mocked_analytics_module.returned_success.call_args.args


@pytest.mark.django_db
def test_index_ineligible(client):
    path = reverse(ROUTE_INDEX)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
def test_reenrollment_error_ineligible(client):
    path = reverse(ROUTE_REENROLLMENT_ERROR)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_reenrollment_error_eligibility_no_error_template(client):
    path = reverse(ROUTE_REENROLLMENT_ERROR)

    with pytest.raises(Exception, match="Re-enrollment error with null template"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier")
def test_reenrollment_error(client, model_EligibilityType_supports_expiration, mocked_session_eligibility):
    mocked_session_eligibility.return_value = model_EligibilityType_supports_expiration

    path = reverse(ROUTE_REENROLLMENT_ERROR)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EligibilityType_supports_expiration.reenrollment_error_template


@pytest.mark.django_db
def test_retry_ineligible(client):
    path = reverse(ROUTE_RETRY)

    response = client.post(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_retry_get(client, mocked_analytics_module):
    path = reverse(ROUTE_RETRY)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_RETRY
    mocked_analytics_module.returned_retry.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_retry_valid_form(client, mocked_analytics_module):
    path = reverse(ROUTE_RETRY)
    response = client.post(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_RETRY
    mocked_analytics_module.returned_retry.assert_called_once()


@pytest.mark.django_db
def test_success_no_verifier(client):
    path = reverse(ROUTE_SUCCESS)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_success_authentication_logged_in(mocker, client, model_TransitAgency, model_EligibilityType):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = True
    mock_session.agency.return_value = model_TransitAgency
    mock_session.eligibility.return_value = model_EligibilityType

    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EligibilityType.enrollment_success_template
    assert {"origin": reverse(ROUTE_LOGGED_OUT)} in mock_session.update.call_args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_success_authentication_not_logged_in(mocker, client, model_TransitAgency, model_EligibilityType):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = False
    mock_session.agency.return_value = model_TransitAgency
    mock_session.eligibility.return_value = model_EligibilityType

    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EligibilityType.enrollment_success_template


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier_auth_not_required")
def test_success_no_authentication(mocker, client, model_EligibilityType):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.eligibility.return_value = model_EligibilityType
    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EligibilityType.enrollment_success_template
