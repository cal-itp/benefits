from enum import Enum

from django.shortcuts import redirect
import sentry_sdk

from benefits.routes import routes
from benefits.core import models, session
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


def handle_enrollment_results(request, status: Status, exception: Exception):
    match (status):
        case Status.SUCCESS:
            agency = session.agency(request)
            flow = session.flow(request)
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
                enrollment_method=models.EnrollmentMethods.DIGITAL,
                verified_by=flow.eligibility_verifier,
                expiration_datetime=expiry,
                extra_claims=str_extra_claims,
            )
            event.save()
            analytics.returned_success(request, flow.group_id, extra_claims=oauth_extra_claims)
            return redirect(routes.ENROLLMENT_SUCCESS)

        case Status.SYSTEM_ERROR:
            analytics.returned_error(request, str(exception))
            sentry_sdk.capture_exception(exception)
            return redirect(routes.ENROLLMENT_SYSTEM_ERROR)

        case Status.EXCEPTION:
            analytics.returned_error(request, str(exception))
            raise exception

        case Status.REENROLLMENT_ERROR:
            analytics.returned_error(request, "Re-enrollment error.")
            return redirect(routes.ENROLLMENT_REENROLLMENT_ERROR)
