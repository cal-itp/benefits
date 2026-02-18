"""
The core application: view definition for the root of the webapp.
"""

from dataclasses import asdict, dataclass

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.edit import FormView

from benefits.core import models, session
from benefits.core.context_processors import formatted_gettext_lazy as _
from benefits.core.forms import ChooseAgencyForm
from benefits.core.middleware import pageview_decorator, user_error
from benefits.core.models import EligibilityApiVerificationRequest, SystemName
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
        short_name = self.kwargs.get("agency").short_name
        headline = _("Get your reduced fare when you tap to ride on {short_name}", short_name=short_name)
        context |= {"headline": headline}
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
        # in the URL, a TransitAgency argument is required, but we just need to return the single
        # EligibilityApiVerificationRequest client public key that is shared across all agencies
        eligibility_api_public_key_data = EligibilityApiVerificationRequest.objects.first().client_public_key_data
        return HttpResponse(eligibility_api_public_key_data, content_type="text/plain")


@dataclass
class FlowHelp:

    id: str
    headline: str
    text: str

    def dict(self):
        return asdict(self)


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
        else:
            agency = session.agency(self.request)

            # build up a single list of all flow help contexts
            flows_help = []
            for flow in agency.enrollment_flows.all():
                help_contexts = self.get_help_contexts(flow)
                if help_contexts:
                    flows_help.extend(help_contexts)

            context["flows_help"] = flows_help

        return context

    def get_help_contexts(self, flow) -> list[dict]:
        flows_help = {
            SystemName.CALFRESH.value: [
                FlowHelp(
                    id="calfresh-transit-benefit",
                    headline=_("How do I know if I’m eligible for the transit benefit for CalFresh Cardholders?"),
                    text=_(
                        "We verify your eligibility as a CalFresh Cardholder by confirming you have received funds in your "
                        "CalFresh account at any point in the last three months. This means you are eligible for a transit "
                        "benefit even if you did not receive funds in your CalFresh account this month or last month."
                    ),
                ),
                FlowHelp(
                    id="calfresh-transit-benefit-no-account-changes",
                    headline=_("Will this transit benefit change my CalFresh account?"),
                    text=_("No. Your monthly CalFresh allotment will not change."),
                ),
                FlowHelp(
                    id="calfresh-transit-benefit-enrollment",
                    headline=_("Do I need my Golden State Advantage card to enroll?"),
                    text=_(
                        "No, you do not need your physical EBT card to enroll. We use information from Login.gov and the "
                        "California Department of Social Services to enroll you in the benefit."
                    ),
                ),
                FlowHelp(
                    id="calfresh-transit-benefit-payment",
                    headline=_("Can I use my Golden State Advantage card to pay for transit rides?"),
                    text=_(
                        "No. You can not use your EBT or P-EBT card to pay for public transportation. "
                        "When you tap to ride, use your personal contactless debit or credit card to pay for public transportation."  # noqa: E501
                    ),
                ),
            ],
            SystemName.COURTESY_CARD.value: [
                FlowHelp(
                    id="mst-agency-card",
                    headline=_("What is a Courtesy Card?"),
                    text=_(
                        "Monterey-Salinas Transit issues Courtesy Cards to riders who qualify for a number of reduced fare programs. "  # noqa: E501
                        "This transit benefit may need to be renewed in the future based on the expiration date of the Courtesy Card. "  # noqa: E501
                        'Learn more at the <a href="https://mst.org/riders-guide/how-to-ride/courtesy-card/" target="_blank" rel="noopener noreferrer">MST Riders Guide</a>.'  # noqa: E501
                    ),
                )
            ],
            SystemName.MEDICARE.value: [
                FlowHelp(
                    id="medicare-transit-benefit",
                    headline=_("How do I know if I qualify for the Medicare Cardholder option?"),
                    text=_(
                        "You qualify for this option if you have a Medicare card. To enroll you will need an account with Medicare.gov. "  # noqa: E501
                        "You will need to sign up for a Medicare.gov account if you do not currently have one. Deceased Medicare cardholders do not qualify."  # noqa: E501
                    ),
                ),
                FlowHelp(
                    id="medicare-transit-benefit-enrollment",
                    headline=_("Do I need my Medicare card to enroll?"),
                    text=_(
                        "No, you do not need your physical Medicare card to enroll in a transit benefit. "
                        "You will need the information on your card to create an account at Medicare.gov if you do not currently have an online account."  # noqa: E501
                    ),
                ),
                FlowHelp(
                    id="medicare-transit-benefit-payment",
                    headline=_("Do I need to bring my Medicare card when I ride public transportation?"),
                    text=_(
                        "No, you do not need your physical Medicare card to use your transit benefit on public transportation. "  # noqa: E501
                        "Once you have enrolled you can use your contactless debit or credit card to tap to ride with a reduced fare."  # noqa: E501
                    ),
                ),
                FlowHelp(
                    id="medicare-transit-benefit-recommended",
                    headline=_("What if I qualify for more than one option?"),
                    text=_(
                        "You can enroll in any option you qualify for. We recommend enrolling in the Medicare Cardholder option if you qualify for it."  # noqa: 501
                    ),
                ),
            ],
            SystemName.REDUCED_FARE_MOBILITY_ID.value: [
                FlowHelp(
                    id="sbmtd-agency-card",
                    headline=_("What is a Reduced Fare Mobility ID?"),
                    text=_(
                        "The Santa Barbara Metropolitan Transit District issues Reduced Fare Mobility ID cards to eligible riders. "  # noqa: E501
                        "This transit benefit may need to be renewed in the future based on the expiration date of the Reduced Fare Mobility ID. "  # noqa: E501
                        'Learn more at the <a href="https://sbmtd.gov/fares-passes/" target="_blank" rel="noopener noreferrer">SBMTD Fares & Passes</a>.'  # noqa: E501
                    ),
                )
            ],
        }

        ctx = flows_help.get(flow.system_name)
        return [c.dict() for c in ctx] if ctx else []


class LoggedOutView(TemplateView):
    """View handler for the final log out confirmation message."""

    template_name = "core/logged-out.html"
