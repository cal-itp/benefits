from django.views.generic import TemplateView

from benefits.eligibility import views as eligibility_views


class IndexView(TemplateView):
    """View for the Metro Mobility Wallet landing page."""

    template_name = "metro_mobility_wallet/index.html"


class EligibilityIndexView(eligibility_views.IndexView):
    pass


class EligibilityStartView(eligibility_views.StartView):
    pass


class EligibilityConfirmView(eligibility_views.ConfirmView):
    pass


class EligibilityUnverifiedView(eligibility_views.UnverifiedView):
    pass


class EnrollmentIndexView(TemplateView):
    pass


class SystemErrorView(TemplateView):
    pass
