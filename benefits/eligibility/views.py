"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.utils.html import format_html
from django.utils.translation import pgettext, gettext as _

from benefits.core import recaptcha, session, viewmodels
from benefits.core.middleware import AgencySessionRequired, LoginRequired, RateLimit, RecaptchaEnabled, VerifierSessionRequired
from benefits.core.models import EligibilityVerifier
from benefits.core.views import ROUTE_HELP
from . import analytics, forms, verify


ROUTE_INDEX = "eligibility:index"
ROUTE_START = "eligibility:start"
ROUTE_LOGIN = "oauth:login"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_UNVERIFIED = "eligibility:unverified"
ROUTE_ENROLLMENT = "enrollment:index"

TEMPLATE_INDEX = "eligibility/index.html"
TEMPLATE_START = "eligibility/start.html"
TEMPLATE_CONFIRM = "eligibility/confirm.html"
TEMPLATE_UNVERIFIED = "eligibility/unverified.html"


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(RecaptchaEnabled)
def index(request):
    """View handler for the eligibility verifier selection form."""

    session.update(request, eligibility_types=[], origin=reverse(ROUTE_INDEX))
    agency = session.agency(request)

    eligibility_start = reverse(ROUTE_START)

    help_page = reverse(ROUTE_HELP)

    page = viewmodels.Page(
        title=_("eligibility.pages.index.title"),
        headline=_("eligibility.pages.index.headline"),
        paragraphs=[
            format_html(_("eligibility.pages.index.p[0]%(info_link)s") % {"info_link": f"{help_page}#what-is-cal-itp"})
        ],
        forms=forms.EligibilityVerifierSelectionForm(agency=agency),
    )

    ctx = page.context_dict()
    ctx["help_page"] = help_page
    ctx["help_text"] = format_html(
        _("eligibility.pages.index.help_text%(help_link)s") % {"help_link": f"{help_page}#what-is-cal-itp"}
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
            if recaptcha.has_error(form):
                messages.error(request, "Recaptcha failed. Please try again.")
            page.forms = [form]
            response = TemplateResponse(request, TEMPLATE_INDEX, ctx)
    else:
        if agency.eligibility_verifiers.count() == 1:
            verifier = agency.eligibility_verifiers.first()
            session.update(request, verifier=verifier)
            response = redirect(eligibility_start)
        else:
            response = TemplateResponse(request, TEMPLATE_INDEX, ctx)

    return response


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(VerifierSessionRequired)
def start(request):
    """View handler for the eligibility verification getting started screen."""

    verifier = session.verifier(request)
    button = viewmodels.Button.primary(text=_("eligibility.buttons.continue"), url=reverse(ROUTE_CONFIRM))

    # define the verifier-specific required item
    identity_item = viewmodels.MediaItem(
        icon=viewmodels.Icon("idcardcheck", pgettext("image alt text", "core.icons.idcardcheck")),
        heading=_(verifier.start_item_heading),
        details=_(verifier.start_item_details),
    )

    if verifier.is_auth_required:
        if verifier.uses_auth_verification:
            identity_item.bullets = [
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
    bank_card_item = viewmodels.MediaItem(
        icon=viewmodels.Icon("bankcardcheck", pgettext("image alt text", "core.icons.bankcardcheck")),
        heading=_("eligibility.pages.start.bankcard.title"),
        details=_("eligibility.pages.start.bankcard.text"),
    )

    media = [identity_item, bank_card_item]

    page = viewmodels.Page(
        title=_("eligibility.pages.start.title"),
        headline=_(verifier.start_headline),
        paragraphs=[_(verifier.start_blurb)],
        button=button,
    )

    ctx = page.context_dict()
    ctx["previous_page_button"] = viewmodels.Button.previous_page(url=reverse(ROUTE_INDEX))
    ctx["start_sub_headline"] = _(verifier.start_sub_headline)
    ctx["media"] = media
    ctx["help_link"] = reverse(ROUTE_HELP)

    # update origin now, after we've saved the previous page
    session.update(request, eligibility_types=[], origin=reverse(ROUTE_START))

    return TemplateResponse(request, TEMPLATE_START, ctx)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
@decorator_from_middleware(RateLimit)
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
    types_to_verify = verify.typenames_to_verify(agency, verifier)

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
    types_to_verify = verify.typenames_to_verify(agency, verifier)

    analytics.returned_fail(request, types_to_verify)

    # tel: link to agency phone number
    buttons = viewmodels.Button.agency_contact_links(agency)
    buttons.append(viewmodels.Button.home(request))

    page = viewmodels.Page(
        title=_(verifier.unverified_title),
        headline=_(verifier.unverified_headline),
        icon=viewmodels.Icon("idcardquestion", pgettext("image alt text", "core.icons.idcardquestion")),
        paragraphs=[_(verifier.unverified_blurb)],
        buttons=buttons,
    )

    return TemplateResponse(request, TEMPLATE_UNVERIFIED, page.context_dict())
