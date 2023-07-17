import logging

from benefits.core import session
from benefits.core.middleware import VerifierSessionRequired, user_error


logger = logging.getLogger(__name__)


class VerifierUsesAuthVerificationSessionRequired(VerifierSessionRequired):
    """Middleware raises an exception for sessions lacking an eligibility verifier that uses auth verification."""

    def process_request(self, request):
        result = super().process_request(request)
        if result:
            # from the base middleware class, the session didn't have a verifier
            return result

        if session.verifier(request).uses_auth_verification:
            return None
        else:
            logger.debug("Session not configured with eligibility verifier that uses auth verification")
            return user_error(request)
