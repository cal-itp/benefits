"""
The eligibility application: view definitions for the eligibility verification flow.
"""

from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.views.generic import RedirectView, TemplateView

from benefits.routes import routes
from benefits.core import recaptcha, session
from benefits.core.middleware import AgencySessionRequired, RecaptchaEnabled, FlowSessionRequired
from benefits.core.mixins import AgencySessionRequiredMixin, FlowSessionRequiredMixin
from benefits.core.models import EnrollmentFlow
from . import analytics, forms, verify

TEMPLATE_CONFIRM = "eligibility/confirm.html"


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(RecaptchaEnabled)
def index(request):
    """View handler for the enrollment flow selection form."""
    agency = session.agency(request)
    session.update(request, eligible=False, origin=agency.index_url)

    # clear any prior OAuth token as the user is choosing their desired flow
    # this may or may not require OAuth, with a different set of scope/claims than what is already stored
    session.logout(request)

    context = {"form": forms.EnrollmentFlowSelectionForm(agency=agency)}

    if request.method == "POST":
        form = forms.EnrollmentFlowSelectionForm(data=request.POST, agency=agency)

        if form.is_valid():
            flow_id = form.cleaned_data.get("flow")
            flow = EnrollmentFlow.objects.get(id=flow_id)
            session.update(request, flow=flow)

            analytics.selected_flow(request, flow)

            eligibility_start = reverse(routes.ELIGIBILITY_START)
            response = redirect(eligibility_start)
        else:
            # form was not valid, allow for correction/resubmission
            if recaptcha.has_error(form):
                messages.error(request, "Recaptcha failed. Please try again.")
            context["form"] = form
            context.update(agency.eligibility_index_context)
            response = TemplateResponse(request, "eligibility/index.html", context)
    else:
        context.update(agency.eligibility_index_context)
        response = TemplateResponse(request, "eligibility/index.html", context)

    return response


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(FlowSessionRequired)
def start(request):
    """View handler for the eligibility verification getting started screen."""
    session.update(request, eligible=False, origin=reverse(routes.ELIGIBILITY_START))

    flow = session.flow(request)

    return TemplateResponse(request, "eligibility/start.html", flow.eligibility_start_context)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(RecaptchaEnabled)
@decorator_from_middleware(FlowSessionRequired)
def confirm(request):
    """View handler for the eligibility verification form."""

    verified_view = VerifiedView()

    # GET from an already verified user, no need to verify again
    if request.method == "GET" and session.eligible(request):
        return verified_view.setup_and_dispatch(request)

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
            return verified_view.setup_and_dispatch(request)


class VerifiedView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, RedirectView):
    """CBV for verified eligibility.

    Note we do not register a URL for this view, as it should only be used
    after the user's eligibility is verified and not generally accessible.

    GET requests simply forward along as part of the RedirectView logic.

    POST requests represent a new verification success, triggering additional logic.

    `setup_and_dispatch(request)` is a helper for external callers.
    """

    def get_redirect_url(self, *args, **kwargs):
        return reverse(routes.ENROLLMENT_INDEX)

    def post(self, request, *args, **kwargs):
        session.update(request, eligible=True)
        analytics.returned_success(request, self.flow)
        return super().post(request, *args, **kwargs)

    def setup_and_dispatch(self, request, *args, **kwargs):
        self.setup(request)
        return self.dispatch(request, *args, **kwargs)


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
