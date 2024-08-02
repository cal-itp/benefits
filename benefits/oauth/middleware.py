import logging

from django.shortcuts import redirect
import sentry_sdk

from benefits.core import session
from benefits.core.middleware import VerifierSessionRequired, user_error

from . import analytics
from .redirects import ROUTE_SYSTEM_ERROR


logger = logging.getLogger(__name__)


class VerifierUsesAuthVerificationSessionRequired(VerifierSessionRequired):
    """Middleware raises an exception for sessions lacking an eligibility verifier that uses auth verification."""

    def process_request(self, request):
        result = super().process_request(request)
        if result:
            # from the base middleware class, the session didn't have a verifier
            return result

        verifier = session.verifier(request)

        if verifier.uses_claims_verification:
            # all good, the chosen verifier is configured correctly
            return None
        elif not (verifier.eligibility_api_url or verifier.eligibility_form_class):
            # the chosen verifier doesn't have Eligibility API config OR claims provider config
            # this is likely a misconfiguration on the backend, not a user error
            message = f"Verifier with no API or IDP config: {verifier.name} (id={verifier.id})"
            analytics.error(request, message=message, operation=request.path)
            sentry_sdk.capture_exception(Exception(message))
            return redirect(ROUTE_SYSTEM_ERROR)
        else:
            # the chosen verifier was for Eligibility API
            logger.debug("Session not configured with eligibility verifier that uses auth verification")
            return user_error(request)
