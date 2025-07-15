from django.views.generic import TemplateView

from benefits.core import session
from benefits.core.mixins import AgencySessionRequiredMixin


class SystemErrorView(AgencySessionRequiredMixin, TemplateView):
    """CBV for an oauth system error."""

    template_name = "oauth/system_error.html"

    def get(self, request, *args, **kwargs):
        # overwrite origin so that CTA takes user to agency index
        session.update(request, origin=self.agency.index_url)
        return super().get(request, *args, **kwargs)
