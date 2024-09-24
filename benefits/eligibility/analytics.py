"""
The eligibility application: analytics implementation.
"""

from benefits.core import analytics as core, models


class EligibilityEvent(core.Event):
    """Base analytics event for eligibility verification."""

    def __init__(self, request, event_type, flow: models.EnrollmentFlow, enrollment_method=models.EnrollmentMethods.DIGITAL):
        super().__init__(request, event_type, enrollment_method)
        # overwrite core.Event enrollment flow
        self.update_enrollment_flows(flow)


class SelectedFlowEvent(EligibilityEvent):
    """Analytics event representing the user selecting an enrollment flow."""

    def __init__(self, request, flow: models.EnrollmentFlow, enrollment_method=models.EnrollmentMethods.DIGITAL):
        super().__init__(request, "selected enrollment flow", flow, enrollment_method)


class StartedEligibilityEvent(EligibilityEvent):
    """Analytics event representing the beginning of an eligibility verification check."""

    def __init__(self, request, flow: models.EnrollmentFlow, enrollment_method=models.EnrollmentMethods.DIGITAL):
        super().__init__(request, "started eligibility", flow, enrollment_method)


class ReturnedEligibilityEvent(EligibilityEvent):
    """Analytics event representing the end of an eligibility verification check."""

    def __init__(
        self, request, flow: models.EnrollmentFlow, status, error=None, enrollment_method=models.EnrollmentMethods.DIGITAL
    ):
        super().__init__(request, "returned eligibility", flow, enrollment_method)
        status = str(status).lower()
        if status in ("error", "fail", "success"):
            self.update_event_properties(status=status, error=error)


def selected_flow(request, flow: models.EnrollmentFlow, enrollment_method: str = models.EnrollmentMethods.DIGITAL):
    """Send the "selected enrollment flow" analytics event."""
    core.send_event(SelectedFlowEvent(request, flow, enrollment_method=enrollment_method))


def started_eligibility(request, flow: models.EnrollmentFlow, enrollment_method: str = models.EnrollmentMethods.DIGITAL):
    """Send the "started eligibility" analytics event."""
    core.send_event(StartedEligibilityEvent(request, flow, enrollment_method=enrollment_method))


def returned_error(request, flow: models.EnrollmentFlow, error):
    """Send the "returned eligibility" analytics event with an error status."""
    core.send_event(ReturnedEligibilityEvent(request, flow, status="error", error=error))


def returned_fail(request, flow: models.EnrollmentFlow):
    """Send the "returned eligibility" analytics event with a fail status."""
    core.send_event(ReturnedEligibilityEvent(request, flow, status="fail"))


def returned_success(request, flow: models.EnrollmentFlow, enrollment_method: str = models.EnrollmentMethods.DIGITAL):
    """Send the "returned eligibility" analytics event with a success status."""
    core.send_event(ReturnedEligibilityEvent(request, flow, enrollment_method=enrollment_method, status="success"))
