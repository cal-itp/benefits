"""
The eligibility application: analytics implementation.
"""
from benefits.core import analytics as core


class StartedEligibilityEvent(core.Event):
    def __init__(self, request):
        """Analytics event representing the beginning of an eligibility verification check."""
        super().__init__(request, "started eligibility")


class ReturnedEligibilityEvent(core.Event):
    def __init__(self, request, status, error=None):
        """Analytics event representing the end of an eligibility verification check."""
        super().__init__(request, "returned eligibility")
        if str(status).lower() in ("error", "fail", "success"):
            self.update_event_properties(status=status, error=error)


def started_eligibility(request):
    """Send the "started eligibility" analytics event."""
    core.send_event(StartedEligibilityEvent(request))


def returned_error(request, error):
    """Send the "returned eligibility" analytics event with an error status."""
    core.send_event(ReturnedEligibilityEvent(request, status="error", error=error))


def returned_fail(request):
    """Send the "returned eligibility" analytics event with a fail status."""
    core.send_event(ReturnedEligibilityEvent(request, status="fail"))


def returned_success(request):
    """Send the "returned eligibility" analytics event with a success status."""
    core.send_event(ReturnedEligibilityEvent(request, status="success"))
