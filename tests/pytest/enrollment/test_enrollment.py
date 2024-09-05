from datetime import timedelta

import pytest
from django.utils import timezone
from littlepay.api.funding_sources import FundingSourceResponse
from littlepay.api.groups import GroupFundingSourceResponse

from benefits.enrollment.enrollment import (
    _get_group_funding_source,
    _calculate_expiry,
    _is_expired,
    _is_within_reenrollment_window,
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
