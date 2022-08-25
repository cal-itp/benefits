"""
The eligibility application: analytics implementation.
"""
from benefits.core import analytics as core


class EligibilityEvent(core.Event):
    """Base analytics event for eligibility verification."""

    def __init__(self, request, event_type, eligibility_types):
        super().__init__(request, event_type)
        self.update_event_properties(eligibility_types=eligibility_types)


class StartedEligibilityEvent(EligibilityEvent):
    """Analytics event representing the beginning of an eligibility verification check."""

    def __init__(self, request, eligibility_types):
        super().__init__(request, "started eligibility", eligibility_types)


class ReturnedEligibilityEvent(core.Event):
    """Analytics event representing the end of an eligibility verification check."""

    def __init__(self, request, status, error=None):
        super().__init__(request, "returned eligibility")
        if str(status).lower() in ("error", "fail", "success"):
            self.update_event_properties(status=status, error=error)


def started_eligibility(request, eligibility_types):
    """Send the "started eligibility" analytics event."""
    core.send_event(StartedEligibilityEvent(request, eligibility_types))


def returned_error(request, error):
    """Send the "returned eligibility" analytics event with an error status."""
    core.send_event(ReturnedEligibilityEvent(request, status="error", error=error))


def returned_fail(request):
    """Send the "returned eligibility" analytics event with a fail status."""
    core.send_event(ReturnedEligibilityEvent(request, status="fail"))


def returned_success(request):
    """Send the "returned eligibility" analytics event with a success status."""
    core.send_event(ReturnedEligibilityEvent(request, status="success"))
