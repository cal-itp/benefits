"""
The eligibility application: view definitions for the eligibility verification flow.
"""

from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.views.generic import TemplateView, FormView

from benefits.routes import routes
from benefits.core import recaptcha, session
from benefits.core.context.agency import AgencySlug
from benefits.core.context import formatted_gettext_lazy as _
from benefits.core.middleware import AgencySessionRequired, RecaptchaEnabled, FlowSessionRequired
from benefits.core.mixins import AgencySessionRequiredMixin, FlowSessionRequiredMixin, RecaptchaEnabledMixin
from benefits.core.models import EnrollmentFlow
from . import analytics, forms, verify

TEMPLATE_CONFIRM = "eligibility/confirm.html"


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


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(RecaptchaEnabled)
@decorator_from_middleware(FlowSessionRequired)
def confirm(request):
    """View handler for the eligibility verification form."""

    # GET from an already verified user, no need to verify again
    if request.method == "GET" and session.eligible(request):
        return redirect(routes.ENROLLMENT_INDEX)

    agency = session.agency(request)
    flow = session.flow(request)

    form = flow.eligibility_form_instance()

    # GET/POST for Eligibility API verification
    context = {"form": form}

    # GET from an unverified user, present the form
    if request.method == "GET":
        session.update(request, origin=reverse(routes.ELIGIBILITY_CONFIRM))
        return TemplateResponse(request, TEMPLATE_CONFIRM, context)
    # POST form submission, process form data, make Eligibility Verification API call
    elif request.method == "POST":
        analytics.started_eligibility(request, flow)

        form = flow.eligibility_form_instance(data=request.POST)
        # form was not valid, allow for correction/resubmission
        if not form.is_valid():
            if recaptcha.has_error(form):
                messages.error(request, "Recaptcha failed. Please try again.")
            context["form"] = form
            return TemplateResponse(request, TEMPLATE_CONFIRM, context)

        # form is valid, make Eligibility Verification request to get the verified confirmation
        is_verified = verify.eligibility_from_api(flow, form, agency)

        # form was not valid, allow for correction/resubmission
        if is_verified is None:
            analytics.returned_error(request, flow, form.errors)
            context["form"] = form
            return TemplateResponse(request, TEMPLATE_CONFIRM, context)
        # no type was verified
        elif not is_verified:
            return redirect(routes.ELIGIBILITY_UNVERIFIED)
        # type was verified
        else:
            session.update(request, eligible=True)
            analytics.returned_success(request, flow)

            return redirect(routes.ENROLLMENT_INDEX)


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
