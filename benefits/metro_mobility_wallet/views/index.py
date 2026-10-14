from django.views.generic import TemplateView


class IndexView(TemplateView):
    """View for the Metro Mobility Wallet landing page."""

    template_name = "metro_mobility_wallet/index.html"
