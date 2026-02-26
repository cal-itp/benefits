from datetime import datetime, timedelta
from enum import Enum

import sentry_sdk
from django.shortcuts import redirect
from django.utils import timezone

from benefits.core import models, session
from benefits.routes import routes

from . import analytics


class Status(Enum):
    # SUCCESS means the enrollment went through successfully
    SUCCESS = 1

    # SYSTEM_ERROR means the enrollment system encountered an internal error (returned a 500 HTTP status)
    SYSTEM_ERROR = 2

    # EXCEPTION means the enrollment system is working, but something unexpected happened
    # because of a misconfiguration or invalid request from our side
    EXCEPTION = 3

    # REENROLLMENT_ERROR means that the user tried to re-enroll but is not within the reenrollment window
    REENROLLMENT_ERROR = 4


def _is_expired(expiry_date: datetime):
    """Returns whether the passed in datetime is expired or not."""
    return expiry_date <= timezone.now()


def _is_within_reenrollment_window(expiry_date: datetime, enrollment_reenrollment_date: datetime):
    """Returns if we are currently within the reenrollment window."""
    return enrollment_reenrollment_date <= timezone.now() < expiry_date


def _calculate_expiry(expiration_days: int):
    """Returns the expiry datetime, which should be midnight in our configured timezone of the (N + 1)th day from now,
    where N is expiration_days."""
    default_time_zone = timezone.get_default_timezone()
    expiry_date = timezone.localtime(timezone=default_time_zone) + timedelta(days=expiration_days + 1)
    expiry_datetime = expiry_date.replace(hour=0, minute=0, second=0, microsecond=0)

    return expiry_datetime


def handle_enrollment_results(
    request,
    status: Status,
    verified_by: str,
    exception: Exception = None,
    enrollment_method: str = models.EnrollmentMethods.DIGITAL,
    route_reenrollment_error=routes.ENROLLMENT_REENROLLMENT_ERROR,
    route_success=routes.ENROLLMENT_SUCCESS,
    route_system_error=routes.ENROLLMENT_SYSTEM_ERROR,
    card_category: str = None,
    card_scheme: str = None,
):
    flow = session.flow(request)
    agency = session.agency(request)
    group_id = str(session.group(request).group_id)  # needs to be a string for the API call
    match (status):
        case Status.SUCCESS:
            agency = session.agency(request)
            expiry = session.enrollment_expiry(request)
            oauth_extra_claims = session.oauth_extra_claims(request)
            # EnrollmentEvent expects a string value for extra_claims
            if oauth_extra_claims:
                str_extra_claims = ", ".join(oauth_extra_claims)
            else:
                str_extra_claims = ""
            event = models.EnrollmentEvent.objects.create(
                transit_agency=agency,
                enrollment_flow=flow,
                enrollment_method=enrollment_method,
                verified_by=verified_by,
                expiration_datetime=expiry,
                extra_claims=str_extra_claims,
            )
            event.save()
            analytics.returned_success(
                request,
                enrollment_group=group_id,
                transit_processor=agency.transit_processor,
                enrollment_method=enrollment_method,
                extra_claims=oauth_extra_claims,
                card_scheme=card_scheme,
                card_category=card_category,
            )
            return redirect(route_success)

        case Status.SYSTEM_ERROR:
            analytics.returned_error(
                request,
                str(exception),
                enrollment_group=group_id,
                transit_processor=agency.transit_processor,
                enrollment_method=enrollment_method,
            )
            sentry_sdk.capture_exception(exception)
            return redirect(route_system_error)

        case Status.EXCEPTION:
            analytics.returned_error(
                request,
                str(exception),
                enrollment_group=group_id,
                transit_processor=agency.transit_processor,
                enrollment_method=enrollment_method,
            )
            raise exception

        case Status.REENROLLMENT_ERROR:
            analytics.returned_error(
                request,
                "Re-enrollment error.",
                enrollment_group=group_id,
                transit_processor=agency.transit_processor,
                enrollment_method=enrollment_method,
            )
            return redirect(route_reenrollment_error)
