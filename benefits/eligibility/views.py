"""
The eligibility application: view definitions for the eligibility verification flow.
"""

from dataclasses import asdict, dataclass
from typing import Optional

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from benefits.core import recaptcha, session
from benefits.core.context_processors import formatted_gettext_lazy as _
from benefits.core.mixins import (
    AgencySessionRequiredMixin,
    FlowSessionRequiredMixin,
    RecaptchaEnabledMixin,
)
from benefits.core.models import AgencySlug, EnrollmentFlow, SystemName
from benefits.routes import routes

from . import analytics, forms, verify


class EligibilityIndex:
    def __init__(self, form_text):
        if not isinstance(form_text, list):
            form_text = [form_text]

        self.form_text = form_text

    def dict(self):
        return dict(form_text=self.form_text)


class IndexView(AgencySessionRequiredMixin, RecaptchaEnabledMixin, FormView):
    """View handler for the enrollment flow selection form."""

    template_name = "eligibility/index.html"
    form_class = forms.EnrollmentFlowSelectionForm

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs["agency"] = self.agency
        return kwargs

    def get_context_data(self, **kwargs):
        """Add agency-specific context data."""
        context = super().get_context_data(**kwargs)

        eligiblity_index = {
            AgencySlug.CST.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All CST transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
            AgencySlug.EDCTA.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All EDCTA transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                ),
            ),
            AgencySlug.MST.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All MST transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
            AgencySlug.NEVCO.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All Nevada County Connects transit benefits reduce fares "
                    "by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
            AgencySlug.RABA.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All RABA transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
            AgencySlug.ROSEVILLE.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All Roseville transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
            AgencySlug.SACRT.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All SacRT transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
            AgencySlug.SBMTD.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All SBMTD transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
            AgencySlug.SLORTA.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All RTA transit benefits reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
            AgencySlug.VCTC.value: EligibilityIndex(
                form_text=_(
                    "Cal-ITP doesn’t save any of your information. "
                    "All Ventura County Transportation Commission transit benefits "
                    "reduce fares by 50%% for bus service on fixed routes.".replace("%%", "%")
                )
            ),
        }

        context.update(eligiblity_index[self.agency.slug].dict())
        return context

    def get(self, request, *args, **kwargs):
        """Initialize session state before handling the request."""

        session.update(request, eligible=False, origin=self.agency.index_url)
        session.logout(request)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """If the form is valid, set enrollment flow and redirect."""
        flow_id = form.cleaned_data.get("flow")
        flow = EnrollmentFlow.objects.get(id=flow_id)
        session.update(self.request, flow=flow)

        analytics.selected_flow(self.request, flow)
        return redirect(routes.ELIGIBILITY_START)

    def form_invalid(self, form):
        """If the form is invalid, display error messages."""
        if recaptcha.has_error(form):
            messages.error(self.request, "Recaptcha failed. Please try again.")
        return super().form_invalid(form)


@dataclass
class CTAButton:
    text: str
    route: str
    fallback_text: Optional[str] = None
    extra_classes: Optional[str] = None


@dataclass
class EligibilityStart:
    page_title: str
    headline_text: str
    call_to_action_button: CTAButton
    eligibility_item_headline: Optional[str] = None
    eligibility_item_body: Optional[str] = None

    def dict(self):
        return asdict(self)


class LoginGovEligibilityStart(EligibilityStart):
    def __init__(self, page_title, headline_text):
        super().__init__(
            page_title=page_title,
            headline_text=headline_text,
            call_to_action_button=CTAButton(
                text=_("Get started with"),
                fallback_text="Login.gov",
                route=routes.OAUTH_LOGIN,
                extra_classes="login",
            ),
        )


class AgencyCardEligibilityStart(EligibilityStart):
    def __init__(self, headline_text, eligibility_item_headline, eligibility_item_body):
        super().__init__(
            page_title=_("Agency card overview"),
            headline_text=headline_text,
            eligibility_item_headline=eligibility_item_headline,
            eligibility_item_body=eligibility_item_body,
            call_to_action_button=CTAButton(text=_("Continue"), route=routes.ELIGIBILITY_CONFIRM),
        )


class StartView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, TemplateView):
    """CBV for the eligibility verification getting started screen."""

    template_name = "eligibility/start.html"

    def get(self, request, *args, **kwargs):
        session.update(request, eligible=False, origin=reverse(routes.ELIGIBILITY_START))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eligibility_start = {
            SystemName.CALFRESH.value: LoginGovEligibilityStart(
                page_title=_("CalFresh benefit overview"),
                headline_text=_("You selected a CalFresh Cardholder transit benefit."),
            ),
            SystemName.COURTESY_CARD.value: AgencyCardEligibilityStart(
                headline_text=_("You selected a Courtesy Card transit benefit."),
                eligibility_item_headline=_("Your current Courtesy Card number"),
                eligibility_item_body=_(
                    "You do not need to have your physical MST Courtesy Card, but you will need to know the number."
                ),
            ),
            SystemName.MEDICARE.value: EligibilityStart(
                page_title=_("Medicare benefit overview"),
                headline_text=_("You selected a Medicare Cardholder transit benefit."),
                eligibility_item_headline=_("An online account with Medicare.gov"),
                eligibility_item_body=_(
                    "If you do not have an account you will be able to create one using your red, white, and blue Medicare "
                    "card. We use your Medicare.gov account to verify you qualify."
                ),
                call_to_action_button=CTAButton(text=_("Continue to Medicare.gov"), route=routes.OAUTH_LOGIN),
            ),
            SystemName.OLDER_ADULT.value: LoginGovEligibilityStart(
                page_title=_("Older Adult benefit overview"),
                headline_text=_("You selected an Older Adult transit benefit."),
            ),
            SystemName.REDUCED_FARE_MOBILITY_ID.value: AgencyCardEligibilityStart(
                headline_text=_("You selected a Reduced Fare Mobility ID transit benefit."),
                eligibility_item_headline=_("Your current Reduced Fare Mobility ID number"),
                eligibility_item_body=_("You do not need to have your physical card, but you will need to know the number."),
            ),
            SystemName.VETERAN.value: LoginGovEligibilityStart(
                page_title=_("Veterans benefit overview"),
                headline_text=_("You selected a Veteran transit benefit."),
            ),
        }

        context.update(eligibility_start[self.flow.system_name].dict())
        return context


class ConfirmView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, RecaptchaEnabledMixin, FormView):
    """View handler for Eligiblity Confirm form, used only by flows that support Eligibility API verification."""

    template_name = "eligibility/confirm.html"

    def get_form_class(self):
        flow_system_name = self.flow.system_name

        if flow_system_name == SystemName.COURTESY_CARD:
            form_class = forms.MSTCourtesyCard
        elif flow_system_name == SystemName.REDUCED_FARE_MOBILITY_ID:
            form_class = forms.SBMTDMobilityPass
        else:
            raise ValueError(f"The {flow_system_name} flow does not support Eligibility API verification.")

        return form_class

    def get(self, request, *args, **kwargs):
        if not session.eligible(request):
            session.update(request, origin=reverse(routes.ELIGIBILITY_CONFIRM))
            return super().get(request, *args, **kwargs)
        else:
            # an already verified user, no need to verify again
            return redirect(routes.ENROLLMENT_INDEX)

    def post(self, request, *args, **kwargs):
        analytics.started_eligibility(request, self.flow)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        agency = self.agency
        flow = self.flow
        request = self.request

        # make Eligibility Verification request to get the verified confirmation
        is_verified = verify.eligibility_from_api(flow, form, agency)

        # Eligibility API returned errors (so eligibility is unknown), allow for correction/resubmission
        if is_verified is None:
            analytics.returned_error(request, flow, form.errors)
            return self.form_invalid(form)
        # Eligibility API returned that no type was verified
        elif not is_verified:
            return redirect(routes.ELIGIBILITY_UNVERIFIED)
        # Eligibility API returned that type was verified
        else:
            session.update(request, eligible=True)
            analytics.returned_success(request, flow)

            return redirect(routes.ENROLLMENT_INDEX)

    def form_invalid(self, form):
        if recaptcha.has_error(form):
            messages.error(self.request, "Recaptcha failed. Please try again.")

        return self.get(self.request)


@dataclass
class EligibilityUnverified:
    headline_text: str
    body_text: str
    button_text: str

    def dict(self):
        return asdict(self)


class AgencyCardEligibilityUnverified(EligibilityUnverified):
    def __init__(self, agency_card):
        super().__init__(
            headline_text=_("Your card information may not have been entered correctly."),
            body_text=_(
                "The number and last name must be entered exactly as they appear on your {agency_card}. "
                "Please check your card and try again, or contact your transit agency for help.",
                agency_card=agency_card,
            ),
            button_text=_("Try again"),
        )


class UnverifiedView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, TemplateView):
    """CBV for the unverified eligibility page."""

    template_name = "eligibility/unverified.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eligibility_unverified = {
            SystemName.AGENCY_CARD.value: AgencyCardEligibilityUnverified(agency_card=_("CST Agency Card")),
            SystemName.COURTESY_CARD.value: AgencyCardEligibilityUnverified(agency_card=_("MST Courtesy Card")),
            SystemName.REDUCED_FARE_MOBILITY_ID.value: AgencyCardEligibilityUnverified(
                agency_card=_("SBMTD Reduced Fare Mobility ID card")
            ),
        }

        context_object = eligibility_unverified.get(self.flow.system_name)
        context.update(context_object.dict() if context_object else {})
        return context

    def get(self, request, *args, **kwargs):
        analytics.returned_fail(request, self.flow)
        return super().get(request, *args, **kwargs)
