import logging

from django.views.generic import TemplateView

from benefits.core.mixins import AgencySessionRequiredMixin, EligibleSessionRequiredMixin
from benefits.enrollment.views import FlowSessionRequiredMixin

from .routes import routes

logger = logging.getLogger(__name__)


class IndexView(AgencySessionRequiredMixin, EligibleSessionRequiredMixin, FlowSessionRequiredMixin, TemplateView):
    """View for the enrollment landing page."""

    template_name = "enrollment_init/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                # routes.ENROLLMENT_INIT_REGISTER?
                "cta_button": routes.ENROLLMENT_INIT_INDEX,
                "flow": self.flow,
                "transit_processor": {
                    "name": "INIT",
                    "website": "https://www.initse.com/enus/solutions/fare-collection-revenue-management/",
                },
            }
        )
        return context
