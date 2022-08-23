"""
The enrollment application: analytics implementation.
"""
from benefits.core import analytics as core


class CompletedEnrollment(core.Event):
    """Analytics event representing a successfully completed payment processor enrollment."""

    def __init__(self, request):
        super().__init__(request, "completed enrollment")


def completed_enrollment(request):
    """Send the "completed enrollment" analytics event."""
    core.send_event(CompletedEnrollment(request))
