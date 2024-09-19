"""
The eligibility application: analytics implementation.
"""

from benefits.core import analytics as core


class EligibilityEvent(core.Event):
    """Base analytics event for eligibility verification."""

    def __init__(self, request, event_type, flow_name):
        super().__init__(request, event_type)
        # pass a (converted from string to list) flow_name to preserve analytics reporting
        enrollment_flows = [flow_name]
        # overwrite core.Event enrollment_flows
        self.update_event_properties(enrollment_flows=enrollment_flows)
        self.update_user_properties(enrollment_flows=enrollment_flows)


class SelectedVerifierEvent(EligibilityEvent):
    """Analytics event representing the user selecting an eligibility verifier."""

    def __init__(self, request, eligibility_types):
        super().__init__(request, "selected eligibility verifier", eligibility_types)


class StartedEligibilityEvent(EligibilityEvent):
    """Analytics event representing the beginning of an eligibility verification check."""

    def __init__(self, request, enrollment_flows):
        super().__init__(request, "started eligibility", enrollment_flows)


class ReturnedEligibilityEvent(EligibilityEvent):
    """Analytics event representing the end of an eligibility verification check."""

    def __init__(self, request, enrollment_flows, status, error=None):
        super().__init__(request, "returned eligibility", enrollment_flows)
        status = str(status).lower()
        if status in ("error", "fail", "success"):
            self.update_event_properties(status=status, error=error)
        if status == "success":
            self.update_user_properties(enrollment_flows=enrollment_flows)


def selected_verifier(request, enrollment_flows):
    """Send the "selected eligibility verifier" analytics event."""
    core.send_event(SelectedVerifierEvent(request, enrollment_flows))


def started_eligibility(request, enrollment_flows):
    """Send the "started eligibility" analytics event."""
    core.send_event(StartedEligibilityEvent(request, enrollment_flows))


def returned_error(request, enrollment_flows, error):
    """Send the "returned eligibility" analytics event with an error status."""
    core.send_event(ReturnedEligibilityEvent(request, enrollment_flows, status="error", error=error))


def returned_fail(request, enrollment_flows):
    """Send the "returned eligibility" analytics event with a fail status."""
    core.send_event(ReturnedEligibilityEvent(request, enrollment_flows, status="fail"))


def returned_success(request, enrollment_flows):
    """Send the "returned eligibility" analytics event with a success status."""
    core.send_event(ReturnedEligibilityEvent(request, enrollment_flows, status="success"))
