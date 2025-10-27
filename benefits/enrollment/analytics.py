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
        enrollment_group,
        transit_processor,
        error=None,
        enrollment_method=models.EnrollmentMethods.DIGITAL,
        extra_claims=None,
        card_category=None,
        card_scheme=None,
    ):
        super().__init__(request, "returned enrollment", enrollment_method)
        if str(status).lower() in ("error", "retry", "success"):
            self.update_event_properties(status=status)
            self.update_event_properties(enrollment_group=enrollment_group)
            self.update_event_properties(transit_processor=transit_processor)
            if error is not None:
                self.update_event_properties(error=error)
            if extra_claims is not None:
                self.update_event_properties(extra_claims=extra_claims)
            if card_category is not None:
                self.update_event_properties(card_category=card_category)
            if card_scheme is not None:
                self.update_event_properties(card_scheme=card_scheme)


class FailedPretokenizationRequestEvent(core.Event):
    """Analytics event representing a failure to do the pre-tokenization step for card tokenization."""

    def __init__(self, request, transit_processor, status_code=None, enrollment_method=models.EnrollmentMethods.DIGITAL):
        super().__init__(request, "failed pre-tokenization request", enrollment_method)
        self.update_event_properties(transit_processor=transit_processor)
        if status_code is not None:
            self.update_event_properties(status_code=status_code)


def returned_error(
    request,
    error,
    enrollment_group,
    transit_processor,
    enrollment_method: str = models.EnrollmentMethods.DIGITAL,
):
    """Send the "returned enrollment" analytics event with an error status and message."""
    core.send_event(
        ReturnedEnrollmentEvent(
            request,
            status="error",
            enrollment_group=enrollment_group,
            transit_processor=transit_processor,
            error=error,
            enrollment_method=enrollment_method,
        )
    )


def returned_retry(
    request,
    enrollment_group,
    transit_processor,
    enrollment_method: str = models.EnrollmentMethods.DIGITAL,
):
    """Send the "returned enrollment" analytics event with a retry status."""
    core.send_event(
        ReturnedEnrollmentEvent(
            request,
            status="retry",
            enrollment_group=enrollment_group,
            transit_processor=transit_processor,
            enrollment_method=enrollment_method,
        )
    )


def returned_success(
    request,
    enrollment_group,
    transit_processor,
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
            transit_processor=transit_processor,
            enrollment_method=enrollment_method,
            extra_claims=extra_claims,
            card_scheme=card_scheme,
            card_category=card_category,
        )
    )


def failed_pretokenization_request(
    request, transit_processor, status_code=None, enrollment_method: str = models.EnrollmentMethods.DIGITAL
):
    """Send the "failed pre-tokenization request" analytics event with the response status code."""
    core.send_event(
        FailedPretokenizationRequestEvent(
            request, transit_processor=transit_processor, status_code=status_code, enrollment_method=enrollment_method
        )
    )
