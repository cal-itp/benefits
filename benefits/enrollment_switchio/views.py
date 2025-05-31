from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView, View

from benefits.core import models, session
from benefits.core.mixins import EligibleSessionRequiredMixin, AgencySessionRequiredMixin
from benefits.enrollment_switchio.api import Client, EshopResponseMode
from benefits.routes import routes


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
        agency = session.agency(request)
        switchio_config = agency.switchio_config

        client = Client(
            api_url=switchio_config.api_base_url,
            api_key=switchio_config.api_key,
            api_secret=switchio_config.api_secret,
            private_key=switchio_config.private_key,
            client_certificate=switchio_config.client_certificate,
            ca_certificate=switchio_config.ca_certificate,
        )

        route = reverse(routes.ENROLLMENT_SWITCHIO_INDEX)
        redirect_url = _generate_redirect_uri(request, route)

        registration = client.request_registration(
            eshopRedirectUrl=redirect_url,
            mode="register",
            eshopResponseMode=EshopResponseMode.FORM_POST,
            timeout=settings.REQUESTS_TIMEOUT,
        )

        data = {"gateway_url": registration.gtwUrl}
        return JsonResponse(data)


# copied from https://github.com/Office-of-Digital-Services/django-cdt-identity/blob/main/cdt_identity/views.py#L42-L50
def _generate_redirect_uri(request: HttpRequest, redirect_path: str):
    redirect_uri = str(request.build_absolute_uri(redirect_path)).lower()

    # this is a temporary hack to ensure redirect URIs are HTTPS when the app is deployed
    # see https://github.com/cal-itp/benefits/issues/442 for more context
    if not redirect_uri.startswith("http://localhost"):
        redirect_uri = redirect_uri.replace("http://", "https://")

    return redirect_uri
