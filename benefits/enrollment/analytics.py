"""
The enrollment application: analytics implementation.
"""
from benefits.core import analytics as core


class ReturnedEnrollmentEvent(core.Event):
    """Analytics event representing the end of payment processor enrollment request."""

    def __init__(self, request, status, error=None):
        super().__init__(request, "returned enrollment")
        if str(status).lower() in ("retry", "success"):
            self.update_event_properties(status=status, error=error)


def returned_retry(request):
    """Send the "returned enrollment" analyrics event with a retry status."""
    core.send_event(ReturnedEnrollmentEvent(request, status="retry"))


def returned_success(request):
    """Send the "returned enrollment" analytics event with a success status."""
    core.send_event(ReturnedEnrollmentEvent(request, status="success"))
