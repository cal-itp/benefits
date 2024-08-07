import logging

from django.shortcuts import redirect
import sentry_sdk

from benefits.core import session
from benefits.core.middleware import FlowSessionRequired, user_error

from . import analytics
from .redirects import ROUTE_SYSTEM_ERROR


logger = logging.getLogger(__name__)


class FlowUsesClaimsVerificationSessionRequired(FlowSessionRequired):
    """Middleware raises an exception for sessions lacking an enrollment flow that uses claims verification."""

    def process_request(self, request):
        result = super().process_request(request)
        if result:
            # from the base middleware class, the session didn't have an enrollment flow
            return result

        flow = session.flow(request)

        if flow.uses_claims_verification:
            # all good, the chosen flow is configured correctly
            return None
        elif not (flow.eligibility_api_url or flow.eligibility_form_class):
            # the chosen flow doesn't have Eligibility API config OR claims provider config
            # this is likely a misconfiguration on the backend, not a user error
            message = f"Flow with no API or claims config: {flow.name} (id={flow.id})"
            analytics.error(request, message=message, operation=request.path)
            sentry_sdk.capture_exception(Exception(message))
            return redirect(ROUTE_SYSTEM_ERROR)
        else:
            # the chosen flow was for Eligibility API
            logger.debug("Session not configured with enrollment flow that uses claims verification")
            return user_error(request)
