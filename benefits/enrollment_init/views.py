import logging

from django.views.generic import FormView

from benefits.core import models
from benefits.core.context_processors import formatted_gettext_lazy as _
from benefits.core.mixins import AgencySessionRequiredMixin, EligibleSessionRequiredMixin
from benefits.enrollment.views import IndexContextMixin

# from benefits.routes import routes

logger = logging.getLogger(__name__)


# EligibleSessionRequiredMixin
class IndexView(AgencySessionRequiredMixin, EligibleSessionRequiredMixin, IndexContextMixin, FormView):
    """View for the enrollment landing page."""

    enrollment_method = models.EnrollmentMethods.SELF_SERVICE
    template_name = "enrollment_init/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "headline": _("You are eligible for a reduced fare!"),
                "next_step": _("The last step is to register a bank card so you get a reduced fare when you tap."),
                # "cta_button": routes.ENROLLMENT_INIT_REGISTER,
                "flow": self.flow,
                # placeholder pending https://github.com/cal-itp/benefits/issues/4101
                "transit_processor": {
                    "name": "INIT",
                    "website": "https://www.initse.com/enus/solutions/fare-collection-revenue-management/",
                },
            }
        )
        return context
