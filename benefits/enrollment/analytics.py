"""
The enrollment application: analytics implementation.
"""

from benefits.core import analytics as core, models


class ReturnedEnrollmentEvent(core.Event):
    """Analytics event representing the end of transit processor enrollment request."""

    def __init__(
        self,
        request,
        status,
        error=None,
        enrollment_group=None,
        enrollment_method=models.EnrollmentMethods.DIGITAL,
        extra_claims=None,
        card_category=None,
        card_scheme=None,
    ):
        super().__init__(request, "returned enrollment", enrollment_method)
        if str(status).lower() in ("error", "retry", "success"):
            self.update_event_properties(status=status, error=error, extra_claims=extra_claims)
        if enrollment_group is not None:
            self.update_event_properties(enrollment_group=enrollment_group)
        if card_category is not None:
            self.update_event_properties(card_category=card_category)
        if card_scheme is not None:
            self.update_event_properties(card_scheme=card_scheme)


class FailedPretokenizationRequestEvent(core.Event):
    """Analytics event representing a failure to do the pre-tokenization step for card tokenization."""

    def __init__(self, request, status_code=None, enrollment_method=models.EnrollmentMethods.DIGITAL):
        super().__init__(request, "failed pre-tokenization request", enrollment_method)
        if status_code is not None:
            self.update_event_properties(status_code=status_code)


def returned_error(request, error, enrollment_method: str = models.EnrollmentMethods.DIGITAL):
    """Send the "returned enrollment" analytics event with an error status and message."""
    core.send_event(ReturnedEnrollmentEvent(request, status="error", error=error, enrollment_method=enrollment_method))


def returned_retry(request, enrollment_method: str = models.EnrollmentMethods.DIGITAL):
    """Send the "returned enrollment" analytics event with a retry status."""
    core.send_event(ReturnedEnrollmentEvent(request, status="retry", enrollment_method=enrollment_method))


def returned_success(
    request,
    enrollment_group,
    enrollment_method: str = models.EnrollmentMethods.DIGITAL,
    extra_claims=None,
    card_scheme=None,
    card_category=None,
):
    """Send the "returned enrollment" analytics event with a success status."""
    core.send_event(
        ReturnedEnrollmentEvent(
            request,
            status="success",
            enrollment_group=enrollment_group,
            enrollment_method=enrollment_method,
            extra_claims=extra_claims,
            card_scheme=card_scheme,
            card_category=card_category,
        )
    )


def failed_pretokenization_request(request, status_code=None, enrollment_method: str = models.EnrollmentMethods.DIGITAL):
    """Send the "failed pre-tokenization request" analytics event with the response status code."""
    core.send_event(FailedPretokenizationRequestEvent(request, status_code=status_code, enrollment_method=enrollment_method))
