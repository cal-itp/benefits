from datetime import timedelta
from django.urls import reverse
from django.utils import timezone

import pytest
from requests import HTTPError

from benefits.core import models
from benefits.routes import routes
import benefits.enrollment.enrollment
from benefits.enrollment.enrollment import (
    Status,
    _calculate_expiry,
    _is_expired,
    _is_within_reenrollment_window,
    handle_enrollment_results,
)


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment.enrollment)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment.enrollment, "sentry_sdk")


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
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible", "model_LittlepayGroup")
def test_handle_enrollment_results_success_claims(
    mocker,
    app_request,
    mocked_session_oauth_extra_claims,
    model_TransitAgency,
    model_EnrollmentFlow_with_scope_and_claim,
    mocked_analytics_module,
):
    mocked_session_oauth_extra_claims.return_value = ["claim_1", "claim_2"]
    spy = mocker.spy(benefits.enrollment.enrollment.models.EnrollmentEvent.objects, "create")

    response = handle_enrollment_results(app_request, Status.SUCCESS, "verified by")

    spy.assert_called_once_with(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow_with_scope_and_claim,
        enrollment_method=models.EnrollmentMethods.DIGITAL,
        verified_by="verified by",
        expiration_datetime=None,
        extra_claims="claim_1, claim_2",
    )

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SUCCESS)
    mocked_analytics_module.returned_success.assert_called_once()
    analytics_kwargs = mocked_analytics_module.returned_success.call_args.kwargs
    assert analytics_kwargs["enrollment_group"] == model_EnrollmentFlow_with_scope_and_claim.group_id
    assert analytics_kwargs["enrollment_method"] == models.EnrollmentMethods.DIGITAL


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible", "model_LittlepayGroup")
def test_handle_enrollment_results_success_eligibility_api(
    mocker,
    app_request,
    mocked_session_oauth_extra_claims,
    model_TransitAgency,
    model_EnrollmentFlow_with_eligibility_api,
    mocked_analytics_module,
):
    mocked_session_oauth_extra_claims.return_value = ["claim_1", "claim_2"]
    spy = mocker.spy(benefits.enrollment.enrollment.models.EnrollmentEvent.objects, "create")

    response = handle_enrollment_results(app_request, Status.SUCCESS, "verified by")

    spy.assert_called_once_with(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow_with_eligibility_api,
        enrollment_method=models.EnrollmentMethods.DIGITAL,
        verified_by="verified by",
        expiration_datetime=None,
        extra_claims="claim_1, claim_2",
    )

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SUCCESS)
    mocked_analytics_module.returned_success.assert_called_once()
    analytics_kwargs = mocked_analytics_module.returned_success.call_args.kwargs
    assert analytics_kwargs["enrollment_group"] == model_EnrollmentFlow_with_eligibility_api.group_id
    assert analytics_kwargs["enrollment_method"] == models.EnrollmentMethods.DIGITAL


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible", "model_LittlepayGroup")
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
def test_handle_enrollment_results_system_error(
    mocker, app_request, status_code, mocked_analytics_module, mocked_sentry_sdk_module
):
    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error

    mock_exception = HTTPError(response=mock_error_response)

    response = handle_enrollment_results(app_request, Status.SYSTEM_ERROR, "verified by", mock_exception)

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SYSTEM_ERROR)
    mocked_analytics_module.returned_error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible", "model_LittlepayGroup")
def test_handle_enrollment_results_exception(app_request, mocked_analytics_module):
    with pytest.raises(Exception, match=r"some exception"):
        handle_enrollment_results(app_request, Status.EXCEPTION, "verified by", Exception("some exception"))

        mocked_analytics_module.returned_error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible", "model_LittlepayGroup")
def test_handle_enrollment_results_reenrollment_error(app_request, mocked_analytics_module):
    response = handle_enrollment_results(app_request, Status.REENROLLMENT_ERROR, "verified by")

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)
    mocked_analytics_module.returned_error.assert_called_once()
