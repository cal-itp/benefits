"""
The enrollment application: analytics implementation.
"""

from benefits.core import analytics as core


class ReturnedEnrollmentEvent(core.Event):
    """Analytics event representing the end of payment processor enrollment request."""

    def __init__(self, request, status, error=None, payment_group=None):
        super().__init__(request, "returned enrollment")
        if str(status).lower() in ("error", "retry", "success"):
            self.update_event_properties(status=status, error=error)
        if payment_group is not None:
            self.update_event_properties(payment_group=payment_group)


class FailedAccessTokenRequestEvent(core.Event):
    """Analytics event representing a failure to acquire an access token for card tokenization."""

    def __init__(self, request, status_code=None):
        super().__init__(request, "failed access token request")
        if status_code is not None:
            self.update_event_properties(status_code=status_code)


def returned_error(request, error):
    """Send the "returned enrollment" analytics event with an error status and message."""
    core.send_event(ReturnedEnrollmentEvent(request, status="error", error=error))


def returned_retry(request):
    """Send the "returned enrollment" analytics event with a retry status."""
    core.send_event(ReturnedEnrollmentEvent(request, status="retry"))


def returned_success(request, payment_group):
    """Send the "returned enrollment" analytics event with a success status."""
    core.send_event(ReturnedEnrollmentEvent(request, status="success", payment_group=payment_group))


def failed_access_token_request(request, status_code=None):
    """Send the "failed access token request" analytics event with the response status code."""
    core.send_event(FailedAccessTokenRequestEvent(request, status_code=status_code))
