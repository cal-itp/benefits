from django.http import JsonResponse
from django.views.generic import TemplateView, View

from benefits.core import models, session


class IndexView(TemplateView):
    """CBV for the enrollment landing page."""

    template_name = "enrollment_switchio/index--switchio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flow = session.flow(self.request)
        context.update(
            {
                **flow.enrollment_index_context,
                "cta_button": "tokenize_card",
                "enrollment_method": models.EnrollmentMethods.DIGITAL,
            }
        )
        return context


class GatewayUrlView(View):
    """CBV for the tokenization gateway registration"""

    def get(self, request, *args, **kwargs):
        data = {"gateway_url": "https://server/gateway/uuid"}
        return JsonResponse(data)
