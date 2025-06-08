from datetime import timedelta
import json

import pytest
from django.utils import timezone
from littlepay.api.funding_sources import FundingSourceResponse
from littlepay.api.groups import GroupFundingSourceResponse
from requests import HTTPError

from benefits.enrollment.enrollment import Status
from benefits.enrollment_littlepay.enrollment import (
    get_card_types_for_js,
    request_card_tokenization_access,
    enroll,
    _get_group_funding_source,
    _calculate_expiry,
    _is_expired,
    _is_within_reenrollment_window,
)


@pytest.fixture
def mocked_api_base_url(mocker):
    return mocker.patch(
        "benefits.enrollment_littlepay.models.get_secret_by_name", return_value="https://example.com/backend-api"
    )


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


@pytest.fixture
def card_token():
    return "card_token_1234"


@pytest.mark.parametrize("additional_cardtypes", [True, False])
def test_get_card_types_for_js(settings, additional_cardtypes):
    settings.LITTLEPAY_ADDITIONAL_CARDTYPES = additional_cardtypes

    card_types = get_card_types_for_js()
    assert isinstance(card_types, str)

    parsed_card_types = json.loads(card_types)
    assert isinstance(parsed_card_types, list)

    assert "visa" in card_types
    assert "mastercard" in card_types
    if additional_cardtypes:
        assert "discover" in card_types
        assert "amex" in card_types


@pytest.mark.django_db
@pytest.mark.usefixtures("model_EnrollmentFlow")
def test_get_group_funding_sources_funding_source_not_enrolled_yet(mocker, mocked_funding_source):
    mock_client = mocker.Mock()
    mock_client.get_concession_group_linked_funding_sources.return_value = []

    matching_group_funding_source = _get_group_funding_source(mock_client, "group123", mocked_funding_source.id)

    assert matching_group_funding_source is None


@pytest.mark.django_db
@pytest.mark.usefixtures("model_EnrollmentFlow")
def test_get_group_funding_sources_funding_source_already_enrolled(
    mocker, mocked_funding_source, mocked_group_funding_source_no_expiry
):
    mock_client = mocker.Mock()
    mock_client.get_concession_group_linked_funding_sources.return_value = [mocked_group_funding_source_no_expiry]

    matching_group_funding_source = _get_group_funding_source(mock_client, "group123", mocked_funding_source.id)

    assert matching_group_funding_source == mocked_group_funding_source_no_expiry


def test_calculate_expiry():
    expiration_days = 365

    expiry_date = _calculate_expiry(expiration_days)

    assert expiry_date == (
        timezone.localtime(timezone=timezone.get_default_timezone()) + timedelta(days=expiration_days + 1)
    ).replace(hour=0, minute=0, second=0, microsecond=0)


def test_calculate_expiry_specific_date(mocker):
    expiration_days = 14
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=timezone.make_aware(
            value=timezone.datetime(2024, 3, 1, 13, 37, 11, 5), timezone=timezone.get_fixed_timezone(offset=0)
        ),
    )

    expiry_date = _calculate_expiry(expiration_days)

    assert expiry_date == timezone.make_aware(
        value=timezone.datetime(2024, 3, 16, 0, 0, 0, 0), timezone=timezone.get_default_timezone()
    )


def test_is_expired_expiry_date_is_in_the_past(mocker):
    expiry_date = timezone.make_aware(timezone.datetime(2023, 12, 31), timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 10, 30), timezone.get_default_timezone()),
    )

    assert _is_expired(expiry_date)


def test_is_expired_expiry_date_is_in_the_future(mocker):
    expiry_date = timezone.make_aware(timezone.datetime(2024, 1, 1, 17, 34), timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 11, 5), timezone.get_default_timezone()),
    )

    assert not _is_expired(expiry_date)


def test_is_expired_expiry_date_equals_now(mocker):
    expiry_date = timezone.make_aware(timezone.datetime(2024, 1, 1, 13, 37), timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 13, 37), timezone.get_default_timezone()),
    )

    assert _is_expired(expiry_date)


def test_is_within_enrollment_window_True(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 2, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert is_within_reenrollment_window


def test_is_within_enrollment_window_before_window(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 1, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


def test_is_within_enrollment_window_after_window(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 3, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


def test_is_within_enrollment_window_equal_reenrollment_date(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=enrollment_reenrollment_date,
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert is_within_reenrollment_window


def test_is_within_enrollment_window_equal_expiry_date(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment.timezone.now",
        return_value=expiry_date,
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_api_base_url", "mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow_does_not_support_expiration"
)
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
def test_enroll_system_error(
    mocker,
    status_code,
    app_request,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)
    mock_client.link_concession_group_funding_source.side_effect = http_error

    status, exception = enroll(app_request, card_token)

    assert status is Status.SYSTEM_ERROR
    assert exception == http_error


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_api_base_url", "mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow_does_not_support_expiration"
)
def test_enroll_exception_http_error_400(
    mocker,
    app_request,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(
        response=mock_error_response,
    )
    mock_client.link_concession_group_funding_source.side_effect = http_error

    status, exception = enroll(app_request, card_token)

    assert status is Status.EXCEPTION
    assert isinstance(exception, Exception)
    assert exception.args[0] == f"{http_error}: {http_error.response.json()}"


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_api_base_url", "mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow_does_not_support_expiration"
)
def test_enroll_exception_non_http_error(
    mocker,
    app_request,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_client.link_concession_group_funding_source.side_effect = Exception("some other exception")

    status, exception = enroll(app_request, card_token)

    assert status is Status.EXCEPTION
    assert isinstance(exception, Exception)
    assert exception.args[0] == "some other exception"


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_api_base_url", "mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow_does_not_support_expiration"
)
def test_enroll_success_flow_does_not_support_expiration_customer_already_enrolled_no_expiry(
    mocker,
    app_request,
    card_token,
    mocked_funding_source,
    mocked_group_funding_source_no_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    mocker.patch(
        "benefits.enrollment_littlepay.enrollment._get_group_funding_source",
        return_value=mocked_group_funding_source_no_expiry,
    )

    status, exception = enroll(app_request, card_token)

    mock_client.link_concession_group_funding_source.assert_not_called()

    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency", "mocked_session_flow")
def test_enroll_success_flow_does_not_support_expiration_no_expiry(
    mocker,
    app_request,
    model_EnrollmentFlow_does_not_support_expiration,
    card_token,
    mocked_funding_source,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    status, exception = enroll(app_request, card_token)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id, group_id=model_EnrollmentFlow_does_not_support_expiration.group_id
    )
    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency", "mocked_session_flow")
def test_enroll_success_flow_supports_expiration(
    mocker,
    app_request,
    model_EnrollmentFlow_supports_expiration,
    card_token,
    mocked_funding_source,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    status, exception = enroll(app_request, card_token)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert status == Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency", "mocked_session_flow")
def test_enroll_success_flow_supports_expiration_no_expiry(
    mocker,
    app_request,
    model_EnrollmentFlow_supports_expiration,
    card_token,
    mocked_funding_source,
    mocked_group_funding_source_no_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    mocker.patch(
        "benefits.enrollment_littlepay.enrollment._get_group_funding_source",
        return_value=mocked_group_funding_source_no_expiry,
    )

    status, exception = enroll(app_request, card_token)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert status == Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency", "mocked_session_flow")
def test_enroll_success_flow_supports_expiration_is_expired(
    mocker,
    app_request,
    model_EnrollmentFlow_supports_expiration,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment._get_group_funding_source",
        return_value=mocked_group_funding_source_with_expiry,
    )

    mocker.patch("benefits.enrollment_littlepay.enrollment._is_expired", return_value=True)

    status, exception = enroll(app_request, card_token)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency", "mocked_session_flow")
def test_enroll_success_flow_supports_expiration_is_within_reenrollment_window(
    mocker,
    app_request,
    model_EnrollmentFlow_supports_expiration,
    card_token,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment._get_group_funding_source",
        return_value=mocked_group_funding_source_with_expiry,
    )

    mocker.patch("benefits.enrollment_littlepay.enrollment._is_within_reenrollment_window", return_value=True)

    status, exception = enroll(app_request, card_token)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_api_base_url", "mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow_supports_expiration"
)
def test_enroll_reenrollment_error(
    mocker,
    app_request,
    card_token,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment._get_group_funding_source",
        return_value=mocked_group_funding_source_with_expiry,
    )

    mocker.patch("benefits.enrollment_littlepay.enrollment._is_expired", return_value=False)
    mocker.patch("benefits.enrollment_littlepay.enrollment._is_within_reenrollment_window", return_value=False)

    status, exception = enroll(app_request, card_token)

    mock_client.link_concession_group_funding_source.assert_not_called()
    assert status is Status.REENROLLMENT_ERROR
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_api_base_url", "mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow_does_not_support_expiration"
)
def test_enroll_does_not_support_expiration_has_expiration_date(
    mocker,
    app_request,
    card_token,
    mocked_funding_source,
    mocked_group_funding_source_with_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment_littlepay.enrollment._get_group_funding_source",
        return_value=mocked_group_funding_source_with_expiry,
    )

    status, exception = enroll(app_request, card_token)

    assert status is Status.EXCEPTION
    assert isinstance(exception, NotImplementedError)

    # this is what we would assert if removing expiration were supported
    # mock_client.link_concession_group_funding_source.assert_called_once_with(
    #     funding_source_id=mocked_funding_source.id,
    #     group_id=model_EnrollmentFlow_does_not_support_expiration.group_id,
    #     expiry_date=None,
    # )


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency")
def test_request_card_tokenization_access(mocker, app_request):
    mock_response = {}
    mock_response["access_token"] = "123"
    mock_response["expires_at"] = "2024-01-01T00:00:00"

    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.request_card_tokenization_access.return_value = mock_response

    response = request_card_tokenization_access(app_request)

    assert response.status is Status.SUCCESS
    assert response.access_token == "123"
    assert response.expires_at == "2024-01-01T00:00:00"
    assert response.exception is None
    assert response.status_code is None
    mock_client.oauth.ensure_active_token.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency")
def test_request_card_tokenization_access_system_error(mocker, app_request):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=500, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mock_client.request_card_tokenization_access.side_effect = http_error

    response = request_card_tokenization_access(app_request)

    assert response.status is Status.SYSTEM_ERROR
    assert response.access_token is None
    assert response.expires_at is None
    assert response.exception == http_error
    assert response.status_code == 500


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency")
def test_request_card_tokenization_access_http_400_error(mocker, app_request):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mock_client.request_card_tokenization_access.side_effect = http_error

    response = request_card_tokenization_access(app_request)

    assert response.status is Status.EXCEPTION
    assert response.access_token is None
    assert response.expires_at is None
    assert response.exception == http_error
    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency")
def test_request_card_tokenization_access_exception(mocker, app_request):
    mock_client_cls = mocker.patch("benefits.enrollment_littlepay.enrollment.Client")
    mock_client = mock_client_cls.return_value

    exception = Exception("some exception")
    mock_client.request_card_tokenization_access.side_effect = exception

    response = request_card_tokenization_access(app_request)

    assert response.status is Status.EXCEPTION
    assert response.access_token is None
    assert response.expires_at is None
    assert response.exception == exception
    assert response.status_code is None
