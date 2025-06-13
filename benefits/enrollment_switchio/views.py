import logging
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView, View
import sentry_sdk

from benefits.enrollment_switchio.models import SwitchioConfig
from benefits.routes import routes
from benefits.core import models, session
from benefits.core.mixins import EligibleSessionRequiredMixin, AgencySessionRequiredMixin
from benefits.enrollment import analytics
from benefits.enrollment.enrollment import Status
from benefits.enrollment_switchio.enrollment import request_registration, get_registration_status
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
        session = Session(request)
        switchio_config = self.agency.switchio_config

        if session.registration_id is None or session.gateway_url is None:
            return self._request_registration(request, switchio_config, session)
        else:
            response = get_registration_status(switchio_config=switchio_config, registration_id=session.registration_id)

            if response.status is Status.SUCCESS:
                # if the registration session is no longer valid, request a new registration session.
                if response.registration_status.regState in ["expired", "deleted"]:
                    return self._request_registration(request, switchio_config, session)
                else:
                    return self._gateway_url_response(session)
            else:
                logger.debug(f"Error occurred while attempting to get registration status for {session.registration_id}")
                sentry_sdk.capture_exception(response.exception)
                analytics.failed_pretokenization_request(request, response.status_code)

                if response.status is Status.SYSTEM_ERROR:
                    redirect = reverse(routes.ENROLLMENT_SYSTEM_ERROR)
                else:
                    redirect = reverse(routes.SERVER_ERROR)

                data = {"redirect": redirect}
                return JsonResponse(data)

    def _request_registration(self, request: HttpRequest, switchio_config: SwitchioConfig, session: Session) -> JsonResponse:
        response = request_registration(request, switchio_config)

        if response.status is Status.SUCCESS:
            registration = response.registration
            session.registration_id = registration.regId
            session.gateway_url = registration.gtwUrl

            return self._gateway_url_response(session)
        else:
            logger.debug("Error occurred while requesting a tokenization gateway registration", exc_info=response.exception)
            sentry_sdk.capture_exception(response.exception)
            analytics.failed_pretokenization_request(request, response.status_code)

            if response.status is Status.SYSTEM_ERROR:
                redirect = reverse(routes.ENROLLMENT_SYSTEM_ERROR)
            else:
                redirect = reverse(routes.SERVER_ERROR)

            data = {"redirect": redirect}
            return JsonResponse(data)

    def _gateway_url_response(self, session: Session):
        data = {"gateway_url": session.gateway_url}
        return JsonResponse(data)
