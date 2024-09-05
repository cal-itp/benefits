import time

import pytest
from authlib.integrations.base_client.errors import UnsupportedTokenTypeError
from django.urls import reverse

from littlepay.api.funding_sources import FundingSourceResponse
from littlepay.api.groups import GroupFundingSourceResponse
from requests import HTTPError

from benefits.routes import routes
import benefits.enrollment.views
import benefits.enrollment.enrollment
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.enrollment.views import TEMPLATE_SYSTEM_ERROR, TEMPLATE_RETRY


@pytest.fixture
def card_tokenize_form_data():
    return {"card_token": "tokenized_card"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_analytics_module_views(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment.views)


@pytest.fixture
def mocked_analytics_module_enrollment(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment.enrollment)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment.views, "sentry_sdk")


@pytest.fixture
def mocked_sentry_sdk_module_enrollment(mocker):
    return mocker.patch.object(benefits.enrollment.enrollment, "sentry_sdk")


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


@pytest.fixture
def mocked_group_funding_source_no_expiry(mocked_funding_source):
    return GroupFundingSourceResponse(
        id=mocked_funding_source.id,
        created_date=None,
        updated_date=None,
        expiry_date=None,
    )


@pytest.fixture
def mocked_group_funding_source_with_expiry(mocked_funding_source):
    return GroupFundingSourceResponse(
        id=mocked_funding_source.id,
        created_date="2023-01-01T00:00:00Z",
        updated_date="2021-01-01T00:00:00Z",
        expiry_date="2021-01-01T00:00:00Z",
    )


@pytest.mark.django_db
def test_token_ineligible(client):
    path = reverse(routes.ENROLLMENT_TOKEN)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_refresh(mocker, client):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=False)

    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_token = {}
    mock_token["access_token"] = "access_token"
    mock_token["expires_at"] = time.time() + 10000
    mock_client.request_card_tokenization_access.return_value = mock_token

    path = reverse(routes.ENROLLMENT_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == mock_token["access_token"]
    mock_client.oauth.ensure_active_token.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_valid(mocker, client):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=True)
    mocker.patch("benefits.core.session.enrollment_token", return_value="enrollment_token")

    path = reverse(routes.ENROLLMENT_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == "enrollment_token"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_http_error_500(mocker, client, mocked_analytics_module_views, mocked_sentry_sdk_module):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=False)

    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=500, **mock_error)
    mock_error_response.json.return_value = mock_error
    mock_client.request_card_tokenization_access.side_effect = HTTPError(
        response=mock_error_response,
    )

    path = reverse(routes.ENROLLMENT_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.ENROLLMENT_SYSTEM_ERROR)
    mocked_analytics_module_views.failed_access_token_request.assert_called_once()
    assert 500 in mocked_analytics_module_views.failed_access_token_request.call_args.args
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_http_error_400(mocker, client, mocked_analytics_module_views, mocked_sentry_sdk_module):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=False)

    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    mock_client.request_card_tokenization_access.side_effect = HTTPError(
        response=mock_error_response,
    )

    path = reverse(routes.ENROLLMENT_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.SERVER_ERROR)
    mocked_analytics_module_views.failed_access_token_request.assert_called_once()
    assert 400 in mocked_analytics_module_views.failed_access_token_request.call_args.args
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_misconfigured_client_id(mocker, client, mocked_analytics_module_views, mocked_sentry_sdk_module):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=False)

    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value

    mock_client.request_card_tokenization_access.side_effect = UnsupportedTokenTypeError()

    path = reverse(routes.ENROLLMENT_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.SERVER_ERROR)
    mocked_analytics_module_views.failed_access_token_request.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_connection_error(mocker, client, mocked_analytics_module_views, mocked_sentry_sdk_module):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=False)

    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value

    mock_client.oauth.ensure_active_token.side_effect = ConnectionError()

    path = reverse(routes.ENROLLMENT_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.SERVER_ERROR)
    mocked_analytics_module_views.failed_access_token_request.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_get(client, model_EnrollmentFlow):
    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow.enrollment_index_template
    assert "forms" in response.context_data
    assert "cta_button" in response.context_data
    assert "card_tokenize_env" in response.context_data
    assert "card_tokenize_func" in response.context_data
    assert "card_tokenize_url" in response.context_data
    assert "token_field" in response.context_data
    assert "form_retry" in response.context_data
    assert "form_success" in response.context_data
    assert "overlay_language" in response.context_data


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
@pytest.mark.parametrize("LANGUAGE_CODE, overlay_language", [("en", "en"), ("es", "es-419"), ("unsupported", "en")])
def test_index_eligible_get_changed_language(client, LANGUAGE_CODE, overlay_language):
    path = reverse(routes.ENROLLMENT_INDEX)
    client.post(reverse("set_language"), data={"language": LANGUAGE_CODE})
    response = client.get(path)

    assert response.context_data["overlay_language"] == overlay_language


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_invalid_form(client, invalid_form_data):
    path = reverse(routes.ENROLLMENT_INDEX)

    with pytest.raises(Exception, match=r"form"):
        client.post(path, invalid_form_data)


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_http_error_500(
    mocker,
    client,
    mocked_session_agency,
    model_EnrollmentFlow_does_not_support_expiration,
    mocked_analytics_module_enrollment,
    mocked_sentry_sdk_module_enrollment,
    card_tokenize_form_data,
    status_code,
):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.agency.return_value = mocked_session_agency.return_value
    mock_session.flow.return_value = model_EnrollmentFlow_does_not_support_expiration

    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error
    mock_client.link_concession_group_funding_source.side_effect = HTTPError(
        response=mock_error_response,
    )

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.post(path, card_tokenize_form_data)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SYSTEM_ERROR
    assert {"origin": mocked_session_agency.return_value.index_url} in mock_session.update.call_args
    mocked_analytics_module_enrollment.returned_error.assert_called_once()
    mocked_sentry_sdk_module_enrollment.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_http_error_400(mocker, client, card_tokenize_form_data):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    mock_client.link_concession_group_funding_source.side_effect = HTTPError(
        response=mock_error_response,
    )

    path = reverse(routes.ENROLLMENT_INDEX)
    with pytest.raises(Exception, match=mock_error["message"]):
        client.post(path, card_tokenize_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_failure(mocker, client, card_tokenize_form_data):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_client.link_concession_group_funding_source.side_effect = Exception("some other exception")

    path = reverse(routes.ENROLLMENT_INDEX)
    with pytest.raises(Exception, match=r"some other exception"):
        client.post(path, card_tokenize_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_success_does_not_support_expiration_customer_already_enrolled_no_expiry(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module_views,
    model_EnrollmentFlow_does_not_support_expiration,
    mocked_funding_source,
    mocked_group_funding_source_no_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    mocker.patch(
        "benefits.enrollment.enrollment._get_group_funding_source", return_value=mocked_group_funding_source_no_expiry
    )

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.post(path, card_tokenize_form_data)

    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_does_not_support_expiration.enrollment_success_template
    mocked_analytics_module_views.returned_success.assert_called_once()
    assert (
        model_EnrollmentFlow_does_not_support_expiration.group_id
        in mocked_analytics_module_views.returned_success.call_args.args
    )


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_success_does_not_support_expiration_no_expiry(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module_views,
    model_EnrollmentFlow_does_not_support_expiration,
    mocked_funding_source,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id, group_id=model_EnrollmentFlow_does_not_support_expiration.group_id
    )
    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_does_not_support_expiration.enrollment_success_template
    mocked_analytics_module_views.returned_success.assert_called_once()
    assert (
        model_EnrollmentFlow_does_not_support_expiration.group_id
        in mocked_analytics_module_views.returned_success.call_args.args
    )


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_success_supports_expiration(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module_views,
    model_EnrollmentFlow_supports_expiration,
    mocked_funding_source,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_supports_expiration.enrollment_success_template
    mocked_analytics_module_views.returned_success.assert_called_once()
    assert model_EnrollmentFlow_supports_expiration.group_id in mocked_analytics_module_views.returned_success.call_args.args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_success_supports_expiration_no_expiry(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module_views,
    model_EnrollmentFlow_supports_expiration,
    mocked_funding_source,
    mocked_group_funding_source_no_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    mocker.patch(
        "benefits.enrollment.enrollment._get_group_funding_source", return_value=mocked_group_funding_source_no_expiry
    )

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_supports_expiration.enrollment_success_template
    mocked_analytics_module_views.returned_success.assert_called_once()
    assert model_EnrollmentFlow_supports_expiration.group_id in mocked_analytics_module_views.returned_success.call_args.args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_success_supports_expiration_is_expired(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module_views,
    model_EnrollmentFlow_supports_expiration,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment.enrollment._get_group_funding_source", return_value=mocked_group_funding_source_with_expiry
    )

    mocker.patch("benefits.enrollment.enrollment._is_expired", return_value=True)

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_supports_expiration.enrollment_success_template
    mocked_analytics_module_views.returned_success.assert_called_once()
    assert model_EnrollmentFlow_supports_expiration.group_id in mocked_analytics_module_views.returned_success.call_args.args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_success_supports_expiration_is_within_reenrollment_window(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module_views,
    model_EnrollmentFlow_supports_expiration,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment.enrollment._get_group_funding_source", return_value=mocked_group_funding_source_with_expiry
    )

    mocker.patch("benefits.enrollment.enrollment._is_within_reenrollment_window", return_value=True)

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_supports_expiration.enrollment_success_template
    mocked_analytics_module_views.returned_success.assert_called_once()
    assert model_EnrollmentFlow_supports_expiration.group_id in mocked_analytics_module_views.returned_success.call_args.args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_success_supports_expiration_is_not_expired_yet(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module_views,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
    model_EnrollmentFlow_supports_expiration,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment.enrollment._get_group_funding_source", return_value=mocked_group_funding_source_with_expiry
    )

    mocker.patch("benefits.enrollment.enrollment._is_expired", return_value=False)
    mocker.patch("benefits.enrollment.enrollment._is_within_reenrollment_window", return_value=False)

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.post(path, card_tokenize_form_data)

    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_supports_expiration.reenrollment_error_template
    mocked_analytics_module_views.returned_error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_post_valid_form_success_does_not_support_expiration_has_expiration_date(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module_enrollment,
    model_EnrollmentFlow_does_not_support_expiration,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment.enrollment._get_group_funding_source", return_value=mocked_group_funding_source_with_expiry
    )

    path = reverse(routes.ENROLLMENT_INDEX)
    with pytest.raises(NotImplementedError):
        client.post(path, card_tokenize_form_data)

    # this is what we would assert if removing expiration were supported
    #
    # mock_client.link_concession_group_funding_source.assert_called_once_with(
    #     funding_source_id=mocked_funding_source.id,
    #     group_id=model_EnrollmentFlow_does_not_support_expiration.group_id,
    #     expiry_date=None,
    # )
    # assert response.status_code == 200
    # assert response.template_name == model_EnrollmentFlow_does_not_support_expiration.enrollment_success_template
    # mocked_analytics_module_enrollment.returned_success.assert_called_once()
    # assert (
    #     model_EnrollmentFlow_does_not_support_expiration.group_id
    #     in mocked_analytics_module_enrollment.returned_success.call_args.args
    # )


@pytest.mark.django_db
def test_index_ineligible(client):
    path = reverse(routes.ENROLLMENT_INDEX)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
def test_reenrollment_error_ineligible(client):
    path = reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_reenrollment_error_eligibility_no_error_template(client):
    path = reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)

    with pytest.raises(Exception, match="Re-enrollment error with null template"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_reenrollment_error(client, model_EnrollmentFlow_supports_expiration, mocked_session_eligible):
    mocked_session_eligible.return_value = model_EnrollmentFlow_supports_expiration

    path = reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_supports_expiration.reenrollment_error_template


@pytest.mark.django_db
def test_retry_ineligible(client):
    path = reverse(routes.ENROLLMENT_RETRY)

    response = client.post(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_retry_get(client, mocked_analytics_module_views):
    path = reverse(routes.ENROLLMENT_RETRY)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_RETRY
    mocked_analytics_module_views.returned_retry.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_retry_valid_form(client, mocked_analytics_module_views):
    path = reverse(routes.ENROLLMENT_RETRY)
    response = client.post(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_RETRY
    mocked_analytics_module_views.returned_retry.assert_called_once()


@pytest.mark.django_db
def test_success_no_flow(client):
    path = reverse(routes.ENROLLMENT_SUCCESS)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_session_eligible")
def test_success_authentication_logged_in(
    mocker, client, model_TransitAgency, model_EnrollmentFlow, mocked_analytics_module_views
):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = True
    mock_session.agency.return_value = model_TransitAgency
    mock_session.flow.return_value = model_EnrollmentFlow

    path = reverse(routes.ENROLLMENT_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow.enrollment_success_template
    assert {"origin": reverse(routes.LOGGED_OUT)} in mock_session.update.call_args
    mocked_analytics_module_views.returned_success.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_session_eligible")
def test_success_authentication_not_logged_in(
    mocker, client, model_TransitAgency, model_EnrollmentFlow, mocked_analytics_module_views
):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = False
    mock_session.agency.return_value = model_TransitAgency
    mock_session.flow.return_value = model_EnrollmentFlow

    path = reverse(routes.ENROLLMENT_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow.enrollment_success_template
    mocked_analytics_module_views.returned_success.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_success_no_authentication(
    client, mocked_session_flow_does_not_use_claims_verification, mocked_analytics_module_views
):
    path = reverse(routes.ENROLLMENT_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert (
        response.template_name == mocked_session_flow_does_not_use_claims_verification.return_value.enrollment_success_template
    )
    mocked_analytics_module_views.returned_success.assert_called_once()
