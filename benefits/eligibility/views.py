"""
The eligibility application: view definitions for the eligibility verification flow.
"""

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from benefits.core import recaptcha, session
from benefits.core.context import formatted_gettext_lazy as _
from benefits.core.context.agency import AgencySlug
from benefits.core.context.flow import SystemName
from benefits.core.mixins import AgencySessionRequiredMixin, FlowSessionRequiredMixin, RecaptchaEnabledMixin
from benefits.core.models import EnrollmentFlow
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


class StartView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, TemplateView):
    """CBV for the eligibility verification getting started screen."""

    template_name = "eligibility/start.html"

    def get(self, request, *args, **kwargs):
        session.update(request, eligible=False, origin=reverse(routes.ELIGIBILITY_START))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.flow.eligibility_start_context)
        return context


class ConfirmView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, RecaptchaEnabledMixin, FormView):
    """View handler for Eligiblity Confirm form, used only by flows that support Eligibility API verification."""

    template_name = "eligibility/confirm.html"

    def get_form_class(self):
        agency_slug = self.agency.slug
        flow_system_name = self.flow.system_name

        if agency_slug == AgencySlug.CST and flow_system_name == SystemName.AGENCY_CARD:
            form_class = forms.CSTAgencyCard
        elif agency_slug == AgencySlug.MST and flow_system_name == SystemName.COURTESY_CARD:
            form_class = forms.MSTCourtesyCard
        elif agency_slug == AgencySlug.SBMTD and flow_system_name == SystemName.REDUCED_FARE_MOBILITY_ID:
            form_class = forms.SBMTDMobilityPass
        else:
            raise ValueError(
                f"This agency/flow combination does not support Eligibility API verification: {agency_slug}, {flow_system_name}"  # noqa
            )

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


class UnverifiedView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, TemplateView):
    """CBV for the unverified eligibility page."""

    template_name = "eligibility/unverified.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.flow.eligibility_unverified_context)
        return context

    def get(self, request, *args, **kwargs):
        analytics.returned_fail(request, self.flow)
        return super().get(request, *args, **kwargs)
