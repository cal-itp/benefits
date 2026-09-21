from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from requests import HTTPError

import benefits.enrollment.enrollment
from benefits.core import models
from benefits.enrollment.enrollment import (
    EnrollmentDecision,
    Status,
    _calculate_expiry,
    _calculate_reenrollment_start,
    _is_expired,
    _is_within_reenrollment_window,
    handle_enrollment_results,
    resolve_enrollment_decision,
)
from benefits.routes import routes


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


def test_calculate_reenrollment_start():
    expiry_date = timezone.datetime(2026, 9, 16)
    reenrollment_days = 14

    reenrollment_start = _calculate_reenrollment_start(expiry_date, reenrollment_days)

    assert reenrollment_start.year == expiry_date.year
    assert reenrollment_start.month == expiry_date.month
    assert reenrollment_start.day == expiry_date.day - reenrollment_days


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
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_flow", "mocked_session_group", "mocked_session_eligible", "model_LittlepayGroup"
)
def test_handle_enrollment_results_success_claims(
    mocker,
    app_request,
    mocked_session_oauth_extra_claims,
    model_TransitAgency,
    model_EnrollmentFlow_with_scope_and_claim,
    model_LittlepayGroup,
    mocked_analytics_module,
):
    mocked_session_oauth_extra_claims.return_value = ["claim_1", "claim_2"]
    spy = mocker.spy(benefits.enrollment.enrollment.models.EnrollmentEvent.objects, "create")

    response = handle_enrollment_results(app_request, Status.SUCCESS, "verified by")

    spy.assert_called_once_with(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow_with_scope_and_claim,
        enrollment_method=models.EnrollmentMethods.SELF_SERVICE,
        verified_by="verified by",
        expiration_datetime=None,
        extra_claims="claim_1, claim_2",
    )

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SUCCESS)
    mocked_analytics_module.returned_success.assert_called_once()
    analytics_kwargs = mocked_analytics_module.returned_success.call_args.kwargs
    assert analytics_kwargs["enrollment_group"] == str(model_LittlepayGroup.group_id)
    assert analytics_kwargs["enrollment_method"] == models.EnrollmentMethods.SELF_SERVICE


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_group", "model_TransitAgencyGroup")
def test_handle_enrollment_results_success_transitagencygroup(
    mocker,
    app_request,
    model_EnrollmentFlow,
    model_TransitAgency,
    model_TransitAgency_2,
    mocked_analytics_module,
):
    spy = mocker.spy(benefits.enrollment.enrollment.models.EnrollmentEvent.objects, "create")

    handle_enrollment_results(app_request, Status.SUCCESS, "verified by")

    expected_calls = [
        mocker.call(
            transit_agency=model_TransitAgency,
            enrollment_flow=model_EnrollmentFlow,
            enrollment_method=models.EnrollmentMethods.SELF_SERVICE,
            verified_by="verified by",
            expiration_datetime=None,
            extra_claims="",
        ),
        mocker.call(
            transit_agency=model_TransitAgency_2,
            enrollment_flow=model_EnrollmentFlow,
            enrollment_method=models.EnrollmentMethods.SELF_SERVICE,
            verified_by="verified by",
            expiration_datetime=None,
            extra_claims="",
        ),
    ]
    spy.assert_has_calls(expected_calls)
    assert spy.call_count == 2  # assert_has_calls doesn't assert that those are the _only_ calls

    assert mocked_analytics_module.returned_success.call_count == 2
    analytics_kwargs = mocked_analytics_module.returned_success.call_args.kwargs
    assert analytics_kwargs["agency"] == model_TransitAgency_2


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_flow", "mocked_session_group", "mocked_session_eligible", "model_LittlepayGroup"
)
def test_handle_enrollment_results_success_eligibility_api(
    mocker,
    app_request,
    mocked_session_oauth_extra_claims,
    model_TransitAgency,
    model_EnrollmentFlow_with_eligibility_api,
    model_LittlepayGroup,
    mocked_analytics_module,
):
    mocked_session_oauth_extra_claims.return_value = ["claim_1", "claim_2"]
    spy = mocker.spy(benefits.enrollment.enrollment.models.EnrollmentEvent.objects, "create")

    response = handle_enrollment_results(app_request, Status.SUCCESS, "verified by")

    spy.assert_called_once_with(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow_with_eligibility_api,
        enrollment_method=models.EnrollmentMethods.SELF_SERVICE,
        verified_by="verified by",
        expiration_datetime=None,
        extra_claims="claim_1, claim_2",
    )

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SUCCESS)
    mocked_analytics_module.returned_success.assert_called_once()
    analytics_kwargs = mocked_analytics_module.returned_success.call_args.kwargs
    assert analytics_kwargs["enrollment_group"] == str(model_LittlepayGroup.group_id)
    assert analytics_kwargs["enrollment_method"] == models.EnrollmentMethods.SELF_SERVICE


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_flow", "mocked_session_group", "mocked_session_eligible", "model_LittlepayGroup"
)
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
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_flow", "mocked_session_group", "mocked_session_eligible", "model_LittlepayGroup"
)
def test_handle_enrollment_results_exception(app_request, mocked_analytics_module):
    with pytest.raises(Exception, match=r"some exception"):
        handle_enrollment_results(app_request, Status.EXCEPTION, "verified by", Exception("some exception"))

        mocked_analytics_module.returned_error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_flow", "mocked_session_group", "mocked_session_eligible", "model_LittlepayGroup"
)
def test_handle_enrollment_results_reenrollment_error(app_request, mocked_analytics_module):
    response = handle_enrollment_results(app_request, Status.REENROLLMENT_ERROR, "verified by")

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)
    mocked_analytics_module.returned_error.assert_called_once()


@pytest.mark.parametrize("status", [Status.EXCEPTION, Status.REENROLLMENT_ERROR, Status.SUCCESS, Status.SYSTEM_ERROR])
def test_EnrollmentDecision_defaults(status):
    decision = EnrollmentDecision(status=status)

    assert decision.status is status
    assert decision.expiry_to_send is None
    assert decision.expiry_to_store is None
    assert decision.should_enroll is False
    assert decision.should_remove_expiry is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "already_enrolled,existing_expiry,should_enroll,should_remove_expiry",
    [
        (False, None, True, False),
        (True, None, False, False),
        # the specific existing_expiry shouldn't matter here, since this flow doesn't support expiration anyway
        (True, timezone.datetime(2026, 9, 15), False, True),
    ],
)
def test_resolve_enrollment_decision__expiration_not_supported(
    model_EnrollmentFlow_does_not_support_expiration, already_enrolled, existing_expiry, should_enroll, should_remove_expiry
):
    decision = resolve_enrollment_decision(model_EnrollmentFlow_does_not_support_expiration, already_enrolled, existing_expiry)

    assert decision.status is Status.SUCCESS
    assert decision.expiry_to_send is None
    assert decision.expiry_to_store is None
    assert decision.should_enroll is should_enroll
    assert decision.should_remove_expiry is should_remove_expiry


@pytest.mark.django_db
@pytest.mark.parametrize(
    "already_enrolled",
    [True, False],
)
def test_resolve_enrollment_decision__expiration_supported__no_existing_expiry(
    model_EnrollmentFlow_supports_expiration, already_enrolled
):
    expected_expiry = _calculate_expiry(model_EnrollmentFlow_supports_expiration.expiration_days)

    decision = resolve_enrollment_decision(model_EnrollmentFlow_supports_expiration, already_enrolled, existing_expiry=None)

    assert decision.status is Status.SUCCESS
    assert decision.expiry_to_send == expected_expiry
    assert decision.expiry_to_store == expected_expiry
    assert decision.should_enroll is True
    assert decision.should_remove_expiry is False


@pytest.mark.django_db
def test_resolve_enrollment_decision__expiration_supported__future_expiry(mocker, model_EnrollmentFlow_supports_expiration):
    # an arbitrary expiration date that exists on the provider
    existing_expiry = timezone.make_aware(timezone.datetime(2026, 9, 16), timezone.get_default_timezone())
    # a mock "now" time that is well before the expiry
    now = timezone.make_aware(timezone.datetime(2026, 1, 1), timezone.get_default_timezone())
    mocker.patch("benefits.enrollment.enrollment.timezone.now", return_value=now)

    decision = resolve_enrollment_decision(
        model_EnrollmentFlow_supports_expiration, already_enrolled=True, existing_expiry=existing_expiry
    )

    assert decision.status is Status.REENROLLMENT_ERROR
    assert decision.expiry_to_send is None
    assert decision.expiry_to_store == existing_expiry
    assert decision.should_enroll is False
    assert decision.should_remove_expiry is False


@pytest.mark.django_db
def test_resolve_enrollment_decision__expiration_supported__within_reenrollment_window(
    mocker, model_EnrollmentFlow_supports_expiration
):
    # an arbitrary expiration date that exists on the provider
    existing_expiry = timezone.make_aware(timezone.datetime(2026, 9, 16), timezone.get_default_timezone())
    # a mock "now" time that is (halfway) into the renenrollment window
    days_offset = model_EnrollmentFlow_supports_expiration.expiration_reenrollment_days / 2
    now = existing_expiry - timedelta(days=days_offset)
    mocker.patch("benefits.enrollment.enrollment.timezone.now", return_value=now)
    expected_expiry = _calculate_expiry(model_EnrollmentFlow_supports_expiration.expiration_days)

    decision = resolve_enrollment_decision(
        model_EnrollmentFlow_supports_expiration, already_enrolled=True, existing_expiry=existing_expiry
    )

    assert decision.status is Status.SUCCESS
    assert decision.expiry_to_send == expected_expiry
    assert decision.expiry_to_store == expected_expiry
    assert decision.should_enroll is True
    assert decision.should_remove_expiry is False


@pytest.mark.django_db
def test_resolve_enrollment_decision__expiration_supported__past_expiry(mocker, model_EnrollmentFlow_supports_expiration):
    # an arbitrary expiration date that exists on the provider, far in the past
    existing_expiry = timezone.make_aware(timezone.datetime(2026, 1, 1), timezone.get_default_timezone())
    # a mock "now" time that is well after the expiry
    now = timezone.make_aware(timezone.datetime(2026, 9, 16), timezone.get_default_timezone())
    mocker.patch("benefits.enrollment.enrollment.timezone.now", return_value=now)
    expected_expiry = _calculate_expiry(model_EnrollmentFlow_supports_expiration.expiration_days)

    decision = resolve_enrollment_decision(
        model_EnrollmentFlow_supports_expiration, already_enrolled=True, existing_expiry=existing_expiry
    )

    assert decision.status is Status.SUCCESS
    assert decision.expiry_to_send == expected_expiry
    assert decision.expiry_to_store == expected_expiry
    assert decision.should_enroll is True
    assert decision.should_remove_expiry is False
