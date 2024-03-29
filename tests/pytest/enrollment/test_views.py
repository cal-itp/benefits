from datetime import timedelta
import time

from django.urls import reverse
from django.utils import timezone

from littlepay.api.funding_sources import FundingSourceResponse
from littlepay.api.groups import GroupFundingSourceResponse
from requests import HTTPError
import pytest

from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.views import ROUTE_LOGGED_OUT
from benefits.enrollment.views import (
    ROUTE_INDEX,
    ROUTE_TOKEN,
    ROUTE_SUCCESS,
    ROUTE_RETRY,
    TEMPLATE_REENROLLMENT_ERROR,
    TEMPLATE_SUCCESS,
    TEMPLATE_RETRY,
    _get_group_funding_source,
    _calculate_expiry,
    _is_expired,
    _is_within_reenrollment_window,
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
        participant_id=mocked_funding_source.participant_id,
        concession_expiry=None,
        concession_created_at=None,
        concession_updated_at=None,
    )


@pytest.fixture
def mocked_group_funding_source_with_expiry(mocked_funding_source):
    return GroupFundingSourceResponse(
        id=mocked_funding_source.id,
        participant_id=mocked_funding_source.participant_id,
        concession_expiry="2023-01-01T00:00:00Z",
        concession_created_at="2021-01-01T00:00:00Z",
        concession_updated_at="2021-01-01T00:00:00Z",
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
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_http_error(mocker, client, card_tokenize_form_data):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value

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
@pytest.mark.usefixtures("model_EligibilityType")
def test_get_group_funding_sources_funding_source_not_enrolled_yet(mocker, mocked_funding_source):
    mock_client = mocker.Mock()
    mock_client.get_concession_group_linked_funding_sources.return_value = []

    matching_group_funding_source = _get_group_funding_source(mock_client, "group123", mocked_funding_source.id)

    assert matching_group_funding_source is None


@pytest.mark.django_db
@pytest.mark.usefixtures("model_EligibilityType")
def test_get_group_funding_sources_funding_source_already_enrolled(
    mocker, mocked_funding_source, mocked_group_funding_source_no_expiry
):
    mock_client = mocker.Mock()
    mock_client.get_concession_group_linked_funding_sources.return_value = [mocked_group_funding_source_no_expiry]

    matching_group_funding_source = _get_group_funding_source(mock_client, "group123", mocked_funding_source.id)

    assert matching_group_funding_source == mocked_group_funding_source_no_expiry


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success_does_not_support_expiration_customer_already_enrolled_no_expiry(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module,
    model_EligibilityType_does_not_support_expiration,
    mocked_funding_source,
    mocked_group_funding_source_no_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    mocker.patch("benefits.enrollment.views._get_group_funding_source", return_value=mocked_group_funding_source_no_expiry)

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    mocked_analytics_module.returned_success.assert_called_once()
    assert (
        model_EligibilityType_does_not_support_expiration.group_id in mocked_analytics_module.returned_success.call_args.args
    )


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success_does_not_support_expiration_no_expiry(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module,
    model_EligibilityType_does_not_support_expiration,
    mocked_funding_source,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id, group_id=model_EligibilityType_does_not_support_expiration.group_id
    )
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    mocked_analytics_module.returned_success.assert_called_once()
    assert (
        model_EligibilityType_does_not_support_expiration.group_id in mocked_analytics_module.returned_success.call_args.args
    )


def test_calculate_expiry():
    expiration_days = 365

    expiry_date = _calculate_expiry(expiration_days)

    assert expiry_date == (
        timezone.localtime(timezone=timezone.get_default_timezone()) + timedelta(days=expiration_days + 1)
    ).replace(hour=0, minute=0, second=0, microsecond=0)


def test_calculate_expiry_specific_date(mocker):
    expiration_days = 14
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=timezone.make_aware(
            value=timezone.datetime(2024, 3, 1, 13, 37, 11, 5), timezone=timezone.get_fixed_timezone(offset=0)
        ),
    )

    expiry_date = _calculate_expiry(expiration_days)

    assert expiry_date == timezone.make_aware(
        value=timezone.datetime(2024, 3, 16, 0, 0, 0, 0), timezone=timezone.get_default_timezone()
    )


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success_supports_expiration(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module,
    model_EligibilityType_supports_expiration,
    mocked_funding_source,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EligibilityType_supports_expiration.group_id,
        expiry_date=mocked_session_enrollment_expiry.return_value,
    )
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    mocked_analytics_module.returned_success.assert_called_once()
    assert model_EligibilityType_supports_expiration.group_id in mocked_analytics_module.returned_success.call_args.args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success_supports_expiration_no_expiry(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module,
    model_EligibilityType_supports_expiration,
    mocked_funding_source,
    mocked_group_funding_source_no_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    mocker.patch("benefits.enrollment.views._get_group_funding_source", return_value=mocked_group_funding_source_no_expiry)

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EligibilityType_supports_expiration.group_id,
        expiry_date=mocked_session_enrollment_expiry.return_value,
    )
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    mocked_analytics_module.returned_success.assert_called_once()
    assert model_EligibilityType_supports_expiration.group_id in mocked_analytics_module.returned_success.call_args.args


def test_is_expired_concession_expiry_is_in_the_past(mocker):
    concession_expiry = timezone.make_aware(timezone.datetime(2023, 12, 31), timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 10, 30), timezone.get_default_timezone()),
    )

    assert _is_expired(concession_expiry)


def test_is_expired_concession_expiry_is_in_the_future(mocker):
    concession_expiry = timezone.make_aware(timezone.datetime(2024, 1, 1, 17, 34), timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 11, 5), timezone.get_default_timezone()),
    )

    assert not _is_expired(concession_expiry)


def test_is_expired_concession_expiry_equals_now(mocker):
    concession_expiry = timezone.make_aware(timezone.datetime(2024, 1, 1, 13, 37), timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 13, 37), timezone.get_default_timezone()),
    )

    assert _is_expired(concession_expiry)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success_supports_expiration_is_expired(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module,
    model_EligibilityType_supports_expiration,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what concession_expiry is
    mocker.patch("benefits.enrollment.views._get_group_funding_source", return_value=mocked_group_funding_source_with_expiry)

    mocker.patch("benefits.enrollment.views._is_expired", return_value=True)

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EligibilityType_supports_expiration.group_id,
        expiry_date=mocked_session_enrollment_expiry.return_value,
    )
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    mocked_analytics_module.returned_success.assert_called_once()
    assert model_EligibilityType_supports_expiration.group_id in mocked_analytics_module.returned_success.call_args.args


def test_is_within_enrollment_window_True(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    concession_expiry = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 2, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(concession_expiry, enrollment_reenrollment_date)

    assert is_within_reenrollment_window


def test_is_within_enrollment_window_before_window(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    concession_expiry = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 1, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(concession_expiry, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


def test_is_within_enrollment_window_after_window(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    concession_expiry = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 3, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(concession_expiry, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


def test_is_within_enrollment_window_equal_reenrollment_date(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    concession_expiry = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=enrollment_reenrollment_date,
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(concession_expiry, enrollment_reenrollment_date)

    assert is_within_reenrollment_window


def test_is_within_enrollment_window_equal_concession_expiry(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    concession_expiry = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.views.timezone.now",
        return_value=concession_expiry,
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(concession_expiry, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success_supports_expiration_is_within_reenrollment_window(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module,
    model_EligibilityType_supports_expiration,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what concession_expiry is
    mocker.patch("benefits.enrollment.views._get_group_funding_source", return_value=mocked_group_funding_source_with_expiry)

    mocker.patch("benefits.enrollment.views._is_within_reenrollment_window", return_value=True)

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EligibilityType_supports_expiration.group_id,
        expiry_date=mocked_session_enrollment_expiry.return_value,
    )
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    mocked_analytics_module.returned_success.assert_called_once()
    assert model_EligibilityType_supports_expiration.group_id in mocked_analytics_module.returned_success.call_args.args


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency",
    "mocked_session_verifier",
    "mocked_session_eligibility",
    "model_EligibilityType_supports_expiration",
)
def test_index_eligible_post_valid_form_success_supports_expiration_is_not_expired_yet(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what concession_expiry is
    mocker.patch("benefits.enrollment.views._get_group_funding_source", return_value=mocked_group_funding_source_with_expiry)

    mocker.patch("benefits.enrollment.views._is_expired", return_value=False)
    mocker.patch("benefits.enrollment.views._is_within_reenrollment_window", return_value=False)

    path = reverse(ROUTE_INDEX)
    response = client.post(path, card_tokenize_form_data)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_REENROLLMENT_ERROR
    mocked_analytics_module.returned_error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier", "mocked_session_eligibility")
def test_index_eligible_post_valid_form_success_does_not_support_expiration_has_expiration_date(
    mocker,
    client,
    card_tokenize_form_data,
    mocked_analytics_module,
    model_EligibilityType_does_not_support_expiration,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what concession_expiry is
    mocker.patch("benefits.enrollment.views._get_group_funding_source", return_value=mocked_group_funding_source_with_expiry)

    path = reverse(ROUTE_INDEX)
    with pytest.raises(NotImplementedError):
        client.post(path, card_tokenize_form_data)

    # this is what we would assert if removing expiration were supported
    #
    # mock_client.link_concession_group_funding_source.assert_called_once_with(
    #     funding_source_id=mocked_funding_source.id,
    #     group_id=model_EligibilityType_does_not_support_expiration.group_id,
    #     expiry_date=None,
    # )
    # assert response.status_code == 200
    # assert response.template_name == TEMPLATE_SUCCESS
    # mocked_analytics_module.returned_success.assert_called_once()
    # assert (
    #     model_EligibilityType_does_not_support_expiration.group_id in mocked_analytics_module.returned_success.call_args.args
    # )


@pytest.mark.django_db
def test_index_ineligible(client):
    path = reverse(ROUTE_INDEX)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
def test_retry_ineligible(client):
    path = reverse(ROUTE_RETRY)

    response = client.post(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


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

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_success_authentication_logged_in(mocker, client, model_TransitAgency):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = True
    mock_session.agency.return_value = model_TransitAgency

    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
    assert {"origin": reverse(ROUTE_LOGGED_OUT)} in mock_session.update.call_args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_success_authentication_not_logged_in(mocker, client, model_TransitAgency):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = False
    mock_session.agency.return_value = model_TransitAgency

    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_verifier_auth_not_required")
def test_success_no_authentication(client):
    path = reverse(ROUTE_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_SUCCESS
