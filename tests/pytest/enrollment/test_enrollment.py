from datetime import timedelta

import pytest
from django.utils import timezone
from littlepay.api.funding_sources import FundingSourceResponse
from littlepay.api.groups import GroupFundingSourceResponse
from requests import HTTPError

import benefits.enrollment.enrollment
from benefits.enrollment.enrollment import (
    Status,
    enroll,
    _get_group_funding_source,
    _calculate_expiry,
    _is_expired,
    _is_within_reenrollment_window,
)


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment.enrollment)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
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


@pytest.fixture
def card_token():
    return "card_token_1234"


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
        "benefits.enrollment.enrollment.timezone.now",
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
        "benefits.enrollment.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 10, 30), timezone.get_default_timezone()),
    )

    assert _is_expired(expiry_date)


def test_is_expired_expiry_date_is_in_the_future(mocker):
    expiry_date = timezone.make_aware(timezone.datetime(2024, 1, 1, 17, 34), timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 11, 5), timezone.get_default_timezone()),
    )

    assert not _is_expired(expiry_date)


def test_is_expired_expiry_date_equals_now(mocker):
    expiry_date = timezone.make_aware(timezone.datetime(2024, 1, 1, 13, 37), timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2024, 1, 1, 13, 37), timezone.get_default_timezone()),
    )

    assert _is_expired(expiry_date)


def test_is_within_enrollment_window_True(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 2, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert is_within_reenrollment_window


def test_is_within_enrollment_window_before_window(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 1, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


def test_is_within_enrollment_window_after_window(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.enrollment.timezone.now",
        return_value=timezone.make_aware(timezone.datetime(2023, 3, 15, 15, 30), timezone=timezone.get_default_timezone()),
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


def test_is_within_enrollment_window_equal_reenrollment_date(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.enrollment.timezone.now",
        return_value=enrollment_reenrollment_date,
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert is_within_reenrollment_window


def test_is_within_enrollment_window_equal_expiry_date(mocker):
    enrollment_reenrollment_date = timezone.make_aware(timezone.datetime(2023, 2, 1), timezone=timezone.get_default_timezone())
    expiry_date = timezone.make_aware(timezone.datetime(2023, 3, 1), timezone=timezone.get_default_timezone())

    # mock datetime of "now" to be specific date for testing
    mocker.patch(
        "benefits.enrollment.enrollment.timezone.now",
        return_value=expiry_date,
    )

    is_within_reenrollment_window = _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date)

    assert not is_within_reenrollment_window


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
def test_enroll_system_error(
    mocker,
    status_code,
    app_request,
    model_TransitAgency,
    model_EnrollmentFlow_does_not_support_expiration,
    card_token,
    mocked_analytics_module,
    mocked_sentry_sdk_module,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error
    mock_client.link_concession_group_funding_source.side_effect = HTTPError(
        response=mock_error_response,
    )

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_does_not_support_expiration, card_token)

    assert status is Status.SYSTEM_ERROR
    assert exception is None
    mocked_analytics_module.returned_error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
def test_enroll_exception_http_error_400(
    mocker,
    app_request,
    model_TransitAgency,
    card_token,
    model_EnrollmentFlow_does_not_support_expiration,
    mocked_analytics_module,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(
        response=mock_error_response,
    )
    mock_client.link_concession_group_funding_source.side_effect = http_error

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_does_not_support_expiration, card_token)

    assert status is Status.EXCEPTION
    assert isinstance(exception, Exception)
    assert exception.args[0] == f"{http_error}: {http_error.response.json()}"
    mocked_analytics_module.returned_error.assert_called_once()


@pytest.mark.django_db
def test_enroll_exception_non_http_error(
    mocker,
    app_request,
    model_TransitAgency,
    model_EnrollmentFlow_does_not_support_expiration,
    card_token,
    mocked_analytics_module,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_client.link_concession_group_funding_source.side_effect = Exception("some other exception")

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_does_not_support_expiration, card_token)

    assert status is Status.EXCEPTION
    assert isinstance(exception, Exception)
    assert exception.args[0] == "some other exception"
    mocked_analytics_module.returned_error.assert_called_once()


@pytest.mark.django_db
def test_enroll_success_flow_does_not_support_expiration_customer_already_enrolled_no_expiry(
    mocker,
    app_request,
    model_TransitAgency,
    model_EnrollmentFlow_does_not_support_expiration,
    card_token,
    mocked_funding_source,
    mocked_group_funding_source_no_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    mocker.patch(
        "benefits.enrollment.enrollment._get_group_funding_source", return_value=mocked_group_funding_source_no_expiry
    )

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_does_not_support_expiration, card_token)

    mock_client.link_concession_group_funding_source.assert_not_called()

    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
def test_enroll_success_flow_does_not_support_expiration_no_expiry(
    mocker,
    app_request,
    model_TransitAgency,
    model_EnrollmentFlow_does_not_support_expiration,
    card_token,
    mocked_funding_source,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_does_not_support_expiration, card_token)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id, group_id=model_EnrollmentFlow_does_not_support_expiration.group_id
    )
    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
def test_enroll_success_flow_supports_expiration(
    mocker,
    app_request,
    model_TransitAgency,
    model_EnrollmentFlow_supports_expiration,
    card_token,
    mocked_funding_source,
    mocked_session_enrollment_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_supports_expiration, card_token)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert status == Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
def test_enroll_success_flow_supports_expiration_no_expiry(
    mocker,
    app_request,
    model_TransitAgency,
    model_EnrollmentFlow_supports_expiration,
    card_token,
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

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_supports_expiration, card_token)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert status == Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_flow"
)  # reenrollment window is calculated by reading reenrollment days from session flow
def test_enroll_success_flow_supports_expiration_is_expired(
    mocker,
    app_request,
    model_TransitAgency,
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

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_supports_expiration, card_token)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
def test_enroll_success_flow_supports_expiration_is_within_reenrollment_window(
    mocker,
    app_request,
    model_TransitAgency,
    model_EnrollmentFlow_supports_expiration,
    card_token,
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

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_supports_expiration, card_token)

    mock_client.update_concession_group_funding_source_expiry.assert_called_once_with(
        funding_source_id=mocked_funding_source.id,
        group_id=model_EnrollmentFlow_supports_expiration.group_id,
        expiry=mocked_session_enrollment_expiry.return_value,
    )
    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
def test_enroll_reenrollment_error(
    mocker,
    app_request,
    model_TransitAgency,
    model_EnrollmentFlow_supports_expiration,
    card_token,
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

    mocker.patch("benefits.enrollment.enrollment._is_expired", return_value=False)
    mocker.patch("benefits.enrollment.enrollment._is_within_reenrollment_window", return_value=False)

    status, exception = enroll(app_request, model_TransitAgency, model_EnrollmentFlow_supports_expiration, card_token)

    mock_client.link_concession_group_funding_source.assert_not_called()
    assert status is Status.REENROLLMENT_ERROR
    assert exception is None
