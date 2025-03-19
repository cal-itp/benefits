"""
The eligibility application: view definitions for the eligibility verification flow.
"""

from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from benefits.routes import routes
from benefits.core import recaptcha, session
from benefits.core.middleware import AgencySessionRequired, LoginRequired, RecaptchaEnabled, FlowSessionRequired
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
@decorator_from_middleware(LoginRequired)
@decorator_from_middleware(RecaptchaEnabled)
@decorator_from_middleware(FlowSessionRequired)
def confirm(request):
    """View handler for the eligibility verification form."""

    # GET from an already verified user, no need to verify again
    if request.method == "GET" and session.eligible(request):
        return verified(request)

    unverified_view = reverse(routes.ELIGIBILITY_UNVERIFIED)

    agency = session.agency(request)
    flow = session.flow(request)

    # GET for OAuth verification
    if request.method == "GET" and flow.uses_claims_verification:
        analytics.started_eligibility(request, flow)

        is_verified = verify.eligibility_from_oauth(flow, session.oauth_claims(request))

        if is_verified:
            return verified(request)
        else:
            return redirect(unverified_view)

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
            return redirect(unverified_view)
        # type was verified
        else:
            return verified(request)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
def verified(request):
    """View handler for the verified eligibility page."""

    flow = session.flow(request)
    analytics.returned_success(request, flow)

    session.update(request, eligible=True)

    return redirect(routes.ENROLLMENT_INDEX)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(FlowSessionRequired)
def unverified(request):
    """View handler for the unverified eligibility page."""

    flow = session.flow(request)

    analytics.returned_fail(request, flow)

    return TemplateResponse(request, "eligibility/unverified.html", flow.eligibility_unverified_context)
