import logging
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView, View
import sentry_sdk

from benefits.routes import routes
from benefits.core import models, session
from benefits.core.mixins import EligibleSessionRequiredMixin, AgencySessionRequiredMixin
from benefits.enrollment import analytics
from benefits.enrollment.enrollment import Status
from benefits.enrollment_switchio.enrollment import request_registration
from benefits.enrollment_switchio.session import Session

logger = logging.getLogger(__name__)


class IndexView(EligibleSessionRequiredMixin, TemplateView):
    """View for the enrollment landing page."""

    template_name = "enrollment_switchio/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        flow = session.flow(self.request)

        context.update(
            {
                **flow.enrollment_index_context,
                "cta_button": "tokenize_card",
                "enrollment_method": models.EnrollmentMethods.DIGITAL,
                "transit_processor": {"name": "Switchio", "website": "https://switchio.com/transport/"},
            }
        )
        return context


class GatewayUrlView(AgencySessionRequiredMixin, EligibleSessionRequiredMixin, View):
    """View for the tokenization gateway registration"""

    def get(self, request: HttpRequest, *args, **kwargs):
        response = request_registration(request, self.agency.switchio_config)

        if response.status is Status.SUCCESS:
            registration = response.registration

            Session(request=request, registration_id=registration.regId)

            data = {"gateway_url": registration.gtwUrl}
            return JsonResponse(data)
        else:
            logger.debug("Error occurred while requesting access token", exc_info=response.exception)
            sentry_sdk.capture_exception(response.exception)
            analytics.failed_access_token_request(request, response.status_code)

            if response.status is Status.SYSTEM_ERROR:
                redirect = reverse(routes.ENROLLMENT_SYSTEM_ERROR)
            else:
                redirect = reverse(routes.SERVER_ERROR)

            data = {"redirect": redirect}
            return JsonResponse(data)
