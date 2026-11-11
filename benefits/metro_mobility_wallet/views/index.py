from django.views.generic import TemplateView

from benefits.metro_mobility_wallet.session import Session


class IndexView(TemplateView):
    """View for the Metro Mobility Wallet landing page."""

    template_name = "metro_mobility_wallet/index.html"

    def get(self, request, *args, **kwargs):
        session = Session(self.request)
        session.accepted_terms = False
        return super().get(request, *args, **kwargs)
