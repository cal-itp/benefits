"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.utils.translation import pgettext, gettext as _

from benefits.core import recaptcha, session, viewmodels
from benefits.core.middleware import AgencySessionRequired, LoginRequired, RecaptchaEnabled, VerifierSessionRequired
from benefits.core.models import EligibilityVerifier
from . import analytics, forms, verify


ROUTE_CORE_INDEX = "core:index"
ROUTE_INDEX = "eligibility:index"
ROUTE_START = "eligibility:start"
ROUTE_LOGIN = "oauth:login"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_UNVERIFIED = "eligibility:unverified"
ROUTE_ENROLLMENT = "enrollment:index"

TEMPLATE_START = "eligibility/start.html"
TEMPLATE_CONFIRM = "eligibility/confirm.html"
TEMPLATE_UNVERIFIED = "eligibility/unverified.html"


@decorator_from_middleware(RecaptchaEnabled)
def index(request, agency=None):
    """View handler for the eligibility verifier selection form."""

    if agency is None:
        # see if session has an agency
        agency = session.agency(request)
        if agency is None:
            page = viewmodels.ErrorPage.user_error(path=request.path)
            return TemplateResponse(request, "200_user_error.html", page.context_dict())
        else:
            session.update(request, eligibility_types=[], origin=agency.index_url)
    else:
        session.update(request, agency=agency, eligibility_types=[], origin=reverse(ROUTE_CORE_INDEX))

    # clear any prior OAuth token as the user is choosing their desired flow
    # this may or may not require OAuth, with a different set of scope/claims than what is already stored
    session.logout(request)

    context = {"form": forms.EligibilityVerifierSelectionForm(agency=agency)}

    if request.method == "POST":
        form = forms.EligibilityVerifierSelectionForm(data=request.POST, agency=agency)

        if form.is_valid():
            verifier_id = form.cleaned_data.get("verifier")
            verifier = EligibilityVerifier.objects.get(id=verifier_id)
            session.update(request, verifier=verifier)

            types_to_verify = agency.type_names_to_verify(verifier)
            analytics.selected_verifier(request, types_to_verify)

            eligibility_start = reverse(ROUTE_START)
            response = redirect(eligibility_start)
        else:
            # form was not valid, allow for correction/resubmission
            if recaptcha.has_error(form):
                messages.error(request, "Recaptcha failed. Please try again.")
            context["form"] = form
            response = TemplateResponse(request, agency.eligibility_index_template, context)
    else:
        response = TemplateResponse(request, agency.eligibility_index_template, context)

    return response


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(VerifierSessionRequired)
def start(request):
    """View handler for the eligibility verification getting started screen."""
    session.update(request, eligibility_types=[], origin=reverse(ROUTE_START))

    verifier = session.verifier(request)
    template = verifier.start_template or TEMPLATE_START

    return TemplateResponse(request, template)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
@decorator_from_middleware(RecaptchaEnabled)
@decorator_from_middleware(VerifierSessionRequired)
def confirm(request):
    """View handler for the eligibility verification form."""

    # GET from an already verified user, no need to verify again
    if request.method == "GET" and session.eligible(request):
        eligibility = session.eligibility(request)
        return verified(request, [eligibility.name])

    unverified_view = reverse(ROUTE_UNVERIFIED)

    agency = session.agency(request)
    verifier = session.verifier(request)
    types_to_verify = agency.type_names_to_verify(verifier)

    # GET for OAuth verification
    if request.method == "GET" and verifier.uses_auth_verification:
        analytics.started_eligibility(request, types_to_verify)

        verified_types = verify.eligibility_from_oauth(verifier, session.oauth_claim(request), agency)
        if verified_types:
            return verified(request, verified_types)
        else:
            return redirect(unverified_view)

    # GET/POST for Eligibility API verification
    page = viewmodels.Page(
        title=_(verifier.form_title),
        headline=_(verifier.form_headline),
        paragraphs=[_(verifier.form_blurb)],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix="", verifier=verifier),
    )

    ctx = page.context_dict()
    ctx["previous_page_button"] = viewmodels.Button.previous_page(url=reverse(ROUTE_START))

    # GET from an unverified user, present the form
    if request.method == "GET":
        return TemplateResponse(request, TEMPLATE_CONFIRM, ctx)
    # POST form submission, process form data, make Eligibility Verification API call
    elif request.method == "POST":
        analytics.started_eligibility(request, types_to_verify)

        form = forms.EligibilityVerificationForm(data=request.POST, verifier=verifier)
        # form was not valid, allow for correction/resubmission
        if not form.is_valid():
            if recaptcha.has_error(form):
                messages.error(request, "Recaptcha failed. Please try again.")

            page.forms = [form]
            ctx.update(page.context_dict())
            return TemplateResponse(request, TEMPLATE_CONFIRM, ctx)

        # form is valid, make Eligibility Verification request to get the verified types
        verified_types = verify.eligibility_from_api(verifier, form, agency)

        # form was not valid, allow for correction/resubmission
        if verified_types is None:
            analytics.returned_error(request, types_to_verify, form.errors)
            page.forms = [form]
            ctx.update(page.context_dict())
            return TemplateResponse(request, TEMPLATE_CONFIRM, ctx)
        # no types were verified
        elif len(verified_types) == 0:
            return redirect(unverified_view)
        # type(s) were verified
        else:
            return verified(request, verified_types)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
def verified(request, verified_types):
    """View handler for the verified eligibility page."""

    analytics.returned_success(request, verified_types)

    session.update(request, eligibility_types=verified_types)

    return redirect(ROUTE_ENROLLMENT)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(VerifierSessionRequired)
def unverified(request):
    """View handler for the unverified eligibility page."""

    agency = session.agency(request)
    verifier = session.verifier(request)
    types_to_verify = agency.type_names_to_verify(verifier)

    analytics.returned_fail(request, types_to_verify)

    agency_links = viewmodels.Button.agency_contact_links(agency)

    page = viewmodels.Page(
        title=_(verifier.unverified_title),
        headline=_("eligibility.pages.unverified.headline"),
        icon=viewmodels.Icon("idcardquestion", pgettext("image alt text", "core.icons.idcardquestion")),
        paragraphs=[_(verifier.unverified_blurb)],
    )

    ctx = page.context_dict()
    ctx["agency_links"] = agency_links

    return TemplateResponse(request, TEMPLATE_UNVERIFIED, ctx)
