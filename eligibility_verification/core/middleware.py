"""
The core application: middleware definitions for request/response cycle.
"""
from eligibility_verification.settings import DEBUG, TRANSIT_AGENCY


class DebugMiddleware():
    """Middleware to configure the debug information for each request."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.key = "debug"

    def __call__(self, request):
        request.session[self.key] = DEBUG
        return self.get_response(request)

    def process_template_response(self, request, response):
        if response.context_data is None:
            response.context_data = {}
        response.context_data[self.key] = DEBUG
        return response


class TransitAgencyMiddleware():
    """Middleware to configure the Transit Agency for each request."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.key = "agency"

    def __call__(self, request):
        request.session[self.key] = TRANSIT_AGENCY
        return self.get_response(request)

    def process_template_response(self, request, response):
        if response.context_data is None:
            response.context_data = {}
        response.context_data[self.key] = TRANSIT_AGENCY
        return response
