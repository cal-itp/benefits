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
from benefits.core.middleware import AgencySessionRequired, LoginRequired, RateLimit, VerifierSessionRequired
from benefits.core.models import EligibilityVerifier
from benefits.core.views import ROUTE_HELP, TEMPLATE_PAGE
from . import analytics, forms, verify


ROUTE_INDEX = "eligibility:index"
ROUTE_START = "eligibility:start"
ROUTE_LOGIN = "oauth:login"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_ENROLLMENT = "enrollment:index"

TEMPLATE_START = "eligibility/start.html"
TEMPLATE_CONFIRM = "eligibility/confirm.html"
TEMPLATE_UNVERIFIED = "eligibility/unverified.html"


@decorator_from_middleware(AgencySessionRequired)
def index(request):
    """View handler for the eligibility verifier selection form."""

    session.update(request, eligibility_types=[], origin=reverse(ROUTE_INDEX))
    agency = session.agency(request)

    eligibility_start = reverse(ROUTE_START)

    page = viewmodels.Page(
        title=_("eligibility.pages.index.title"),
        content_title=_("eligibility.pages.index.content_title"),
        forms=forms.EligibilityVerifierSelectionForm(agency=agency),
    )

    if request.method == "POST":
        form = forms.EligibilityVerifierSelectionForm(data=request.POST, agency=agency)

        if form.is_valid():
            verifier_id = form.cleaned_data.get("verifier")
            verifier = EligibilityVerifier.objects.get(id=verifier_id)
            session.update(request, verifier=verifier)

            response = redirect(eligibility_start)
        else:
            # form was not valid, allow for correction/resubmission
            page.forms = [form]
            response = TemplateResponse(request, TEMPLATE_PAGE, page.context_dict())
    else:
        if agency.eligibility_verifiers.count() == 1:
            verifier = agency.eligibility_verifiers.first()
            session.update(request, verifier=verifier)
            response = redirect(eligibility_start)
        else:
            response = TemplateResponse(request, TEMPLATE_PAGE, page.context_dict())

    return response


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(VerifierSessionRequired)
def start(request):
    """View handler for the eligibility verification getting started screen."""

    session.update(request, eligibility_types=[], origin=reverse(ROUTE_START))
    verifier = session.verifier(request)

    button = viewmodels.Button.primary(text=_("eligibility.buttons.continue"), url=reverse(ROUTE_CONFIRM))

    # define the verifier-specific required item
    identity_item = dict(
        icon=viewmodels.Icon("idcardcheck", pgettext("image alt text", "core.icons.idcardcheck")),
        heading=_(verifier.start_item_name),
        details=_(verifier.start_item_description),
    )

    if verifier.is_auth_required:
        if verifier.uses_auth_verification:
            identity_item["links"] = [
                viewmodels.Button.link(
                    classes="btn-text btn-link",
                    text=_("eligibility.pages.start.mst_login.link_text"),
                    url=f"{reverse(ROUTE_HELP)}#login-gov",
                ),
            ]
            identity_item["bullets"] = [
                _("eligibility.pages.start.mst_login.required_items[0]"),
                _("eligibility.pages.start.mst_login.required_items[1]"),
                _("eligibility.pages.start.mst_login.required_items[2]"),
            ]

        if not session.logged_in(request):
            button = viewmodels.Button.login(
                text=_(verifier.auth_provider.sign_in_button_label),
                url=reverse(ROUTE_LOGIN),
            )

    # define the bank card item
    bank_card_item = dict(
        icon=viewmodels.Icon("bankcardcheck", pgettext("image alt text", "core.icons.bankcardcheck")),
        heading=_("eligibility.pages.start.bankcard.title"),
        details=_("eligibility.pages.start.bankcard.text"),
    )

    media = [identity_item, bank_card_item]

    page = viewmodels.Page(
        title=_("eligibility.pages.start.title"),
        paragraphs=[_(verifier.start_blurb)],
        button=button,
    )

    ctx = page.context_dict()
    ctx["start_headline"] = _(verifier.start_headline)
    ctx["start_sub_headline"] = _(verifier.start_sub_headline)
    ctx["media"] = media

    return TemplateResponse(request, TEMPLATE_START, ctx)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
@decorator_from_middleware(RateLimit)
@decorator_from_middleware(VerifierSessionRequired)
def confirm(request):
    """View handler for the eligibility verification form."""

    # GET from an already verified user, no need to verify again
    if request.method == "GET" and session.eligible(request):
        eligibility = session.eligibility(request)
        return verified(request, [eligibility.name])

    agency = session.agency(request)
    verifier = session.verifier(request)
    types_to_verify = verify.typenames_to_verify(agency, verifier)

    # GET for OAuth verification
    if request.method == "GET" and verifier.uses_auth_verification:
        analytics.started_eligibility(request, types_to_verify)

        verified_types = verify.eligibility_from_oauth(verifier, session.oauth_claim(request), agency)
        if verified_types:
            return verified(request, verified_types)
        else:
            return unverified(request)

    # GET/POST for Eligibility API verification
    page = viewmodels.Page(
        title=_(verifier.form_title),
        content_title=_(verifier.form_content_title),
        paragraphs=[_(verifier.form_blurb)],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix="", verifier=verifier),
    )

    # GET from an unverified user, present the form
    if request.method == "GET":
        return TemplateResponse(request, TEMPLATE_CONFIRM, page.context_dict())
    # POST form submission, process form data, make Eligibility Verification API call
    elif request.method == "POST":
        analytics.started_eligibility(request, types_to_verify)

        form = forms.EligibilityVerificationForm(data=request.POST, verifier=verifier)
        # form was not valid, allow for correction/resubmission
        if not form.is_valid():
            if recaptcha.has_error(form):
                messages.error(request, "Recaptcha failed. Please try again.")

            page.forms = [form]
            return TemplateResponse(request, TEMPLATE_CONFIRM, page.context_dict())

        # form is valid, make Eligibility Verification request to get the verified types
        verified_types = verify.eligibility_from_api(verifier, form, agency)

        # form was not valid, allow for correction/resubmission
        if verified_types is None:
            analytics.returned_error(request, types_to_verify, form.errors)
            page.forms = [form]
            return TemplateResponse(request, TEMPLATE_CONFIRM, page.context_dict())
        # no types were verified
        elif len(verified_types) == 0:
            return unverified(request)
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
    types_to_verify = verify.typenames_to_verify(agency, verifier)

    analytics.returned_fail(request, types_to_verify)

    # tel: link to agency phone number
    buttons = viewmodels.Button.agency_contact_links(agency)
    buttons.append(viewmodels.Button.home(request))

    page = viewmodels.Page(
        title=_(verifier.unverified_title),
        classes="with-agency-links",
        content_title=_(verifier.unverified_content_title),
        icon=viewmodels.Icon("idcardquestion", pgettext("image alt text", "core.icons.idcardquestion")),
        paragraphs=[_(verifier.unverified_blurb)],
        buttons=buttons,
    )

    return TemplateResponse(request, TEMPLATE_UNVERIFIED, page.context_dict())
