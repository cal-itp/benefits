from django.http import HttpRequest, JsonResponse
from django.views.generic import TemplateView, View

from benefits.core import models, session
from benefits.core.mixins import EligibleSessionRequiredMixin, AgencySessionRequiredMixin
from benefits.enrollment_switchio.enrollment import request_registration
from benefits.enrollment_switchio.session import Session


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
        registration = request_registration(request)

        Session(request=request, registration_id=registration.regId)

        data = {"gateway_url": registration.gtwUrl}
        return JsonResponse(data)
