import logging

from django.template.response import TemplateResponse
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)


TEMPLATE_RETRY = "enrollment/retry.html"


class HandleEnrollmentError(MiddlewareMixin):
    """Middleware handles an error in the enrollment process and sends the user to the retry page."""

    def process_request(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error(f"Error caught during enrollment: {e}")
            return TemplateResponse(request, TEMPLATE_RETRY)

        return response
