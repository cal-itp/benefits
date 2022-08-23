"""
The enrollment application: analytics implementation.
"""
from benefits.core import analytics as core


class ReturnedEnrollmentEvent(core.Event):
    """Analytics event representing the end of payment processor enrollment request."""

    def __init__(self, request, status, error=None):
        super().__init__(request, "returned enrollment")
        if str(status).lower() in ("error", "fail", "success"):
            self.update_event_properties(status=status, error=error)


def returned_success(request):
    """Send the "completed enrollment" analytics event."""
    core.send_event(ReturnedEnrollmentEvent(request, status="success"))
