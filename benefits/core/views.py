"""
The core application: view definition for the root of the webapp.
"""

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.edit import FormView

from benefits.core import models, session
from benefits.core.forms import ChooseAgencyForm
from benefits.core.middleware import pageview_decorator, user_error
from benefits.routes import routes


class IndexView(FormView):
    """View handler for the main entry page."""

    template_name = "core/index.html"
    form_class = ChooseAgencyForm

    # this form cannot use an action_url because the redirect is determined
    # *after* user interaction
    def form_valid(self, form):
        self.success_url = form.selected_transit_agency.eligibility_index_url
        return super().form_valid(form)

    @method_decorator(pageview_decorator)
    def get(self, request, *args, **kwargs):
        session.reset(request)
        return super().get(request, *args, **kwargs)


class AgencyIndexView(TemplateView):
    """View handler for an agency entry page."""

    template_name = "core/index--agency.html"

    @method_decorator(pageview_decorator)
    def get(self, request, *args, **kwargs):
        agency = self.kwargs.get("agency")
        session.reset(request)
        session.update(request, agency=agency, origin=agency.index_url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agency = self.kwargs.get("agency")
        context |= agency.index_context
        return context


class AgencyCardView(RedirectView):
    """View handler forwards the request to the agency's Agency Card (e.g. Eligibility API) flow, or returns a user error."""

    pattern_name = routes.ELIGIBILITY_CONFIRM

    @method_decorator(pageview_decorator)
    def get(self, request, *args, **kwargs):
        # keep a reference to the agency before removing from kwargs
        # since the eventual reverse() lookup doesn't expect this key in the kwargs for routes.ELIGIBILITY_CONFIRM
        # self.kwargs still contains the agency if needed
        agency = kwargs.pop("agency")
        session.reset(request)
        session.update(request, agency=agency, origin=agency.index_url)

        eligibility_api_flow = agency.enrollment_flows.exclude(api_request=None).order_by("id").last()
        if eligibility_api_flow:
            session.update(request, flow=eligibility_api_flow)
            return super().get(request, *args, **kwargs)
        else:
            return user_error(request)


class AgencyEligibilityIndexView(RedirectView):
    """View handler forwards the request to the agency's Eligibility Index (e.g. flow selection) page."""

    pattern_name = routes.ELIGIBILITY_INDEX

    @method_decorator(pageview_decorator)
    def get(self, request, *args, **kwargs):
        # keep a reference to the agency before removing from kwargs
        # since the eventual reverse() lookup doesn't expect this key in the kwargs for routes.ELIGIBILITY_INDEX
        # self.kwargs still contains the agency if needed
        agency = kwargs.pop("agency")
        session.reset(request)
        session.update(request, agency=agency, origin=agency.index_url)
        return super().get(request, *args, **kwargs)


class AgencyPublicKeyView(View):
    """View handler returns an agency's public key as plain text."""

    @method_decorator(pageview_decorator)
    def get(self, request, *args, **kwargs):
        agency = kwargs.get("agency")
        return HttpResponse(agency.eligibility_api_public_key_data, content_type="text/plain")


class HelpView(TemplateView):
    """View handler for the help page."""

    template_name = "core/help.html"

    @method_decorator(pageview_decorator)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not session.active_agency(self.request):
            choices = models.CardSchemes.CHOICES
            context["all_card_schemes"] = [choices[card_scheme] for card_scheme in choices.keys()]

        return context


class LoggedOutView(TemplateView):
    """View handler for the final log out confirmation message."""

    template_name = "core/logged-out.html"
