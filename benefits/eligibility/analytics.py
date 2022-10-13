"""
The eligibility application: analytics implementation.
"""
from benefits.core import analytics as core


class EligibilityEvent(core.Event):
    """Base analytics event for eligibility verification."""

    def __init__(self, request, event_type, eligibility_types):
        super().__init__(request, event_type)
        # overwrite core.Event eligibility_types
        self.update_event_properties(eligibility_types=eligibility_types)


class StartedEligibilityEvent(EligibilityEvent):
    """Analytics event representing the beginning of an eligibility verification check."""

    def __init__(self, request, eligibility_types):
        super().__init__(request, "started eligibility", eligibility_types)


class ReturnedEligibilityEvent(EligibilityEvent):
    """Analytics event representing the end of an eligibility verification check."""

    def __init__(self, request, eligibility_types, status, error=None):
        super().__init__(request, "returned eligibility", eligibility_types)
        if str(status).lower() in ("error", "fail", "success"):
            self.update_event_properties(status=status, error=error)


def started_eligibility(request, eligibility_types):
    """Send the "started eligibility" analytics event."""
    core.send_event(StartedEligibilityEvent(request, eligibility_types))


def returned_error(request, eligibility_types, error):
    """Send the "returned eligibility" analytics event with an error status."""
    core.send_event(ReturnedEligibilityEvent(request, eligibility_types, status="error", error=error))


def returned_fail(request, eligibility_types):
    """Send the "returned eligibility" analytics event with a fail status."""
    core.send_event(ReturnedEligibilityEvent(request, eligibility_types, status="fail"))


def returned_success(request, eligibility_types):
    """Send the "returned eligibility" analytics event with a success status."""
    core.send_event(ReturnedEligibilityEvent(request, eligibility_types, status="success"))
