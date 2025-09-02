"""
The eligibility application: view definitions for the eligibility verification flow.
"""

import importlib
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView

from benefits.routes import routes
from benefits.core import recaptcha, session
from benefits.core.context.agency import AgencySlug
from benefits.core.context import formatted_gettext_lazy as _
from benefits.core.mixins import AgencySessionRequiredMixin, FlowSessionRequiredMixin, RecaptchaEnabledMixin
from benefits.core.models import EnrollmentFlow
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
        # inspired by https://stackoverflow.com/a/30941292
        module_name, class_name = self.flow.eligibility_form_class.rsplit(".", 1)
        FormClass = getattr(importlib.import_module(module_name), class_name)

        return FormClass

    def get(self, request, *args, **kwargs):
        if session.eligible(request):
            return redirect(routes.ENROLLMENT_INDEX)
        else:
            session.update(request, origin=reverse(routes.ELIGIBILITY_CONFIRM))
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        analytics.started_eligibility(request, self.flow)

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        agency = self.agency
        flow = self.flow
        request = self.request

        # make Eligibility Verification request to get the verified confirmation
        is_verified = verify.eligibility_from_api(flow, form, agency)

        # form was not valid, allow for correction/resubmission
        if is_verified is None:
            analytics.returned_error(request, flow, form.errors)
            return self.form_invalid(form)
        # no type was verified
        elif not is_verified:
            return redirect(routes.ELIGIBILITY_UNVERIFIED)
        # type was verified
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
