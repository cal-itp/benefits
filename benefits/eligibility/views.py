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

    media = [
        dict(
            icon=viewmodels.Icon("bankcardcheck", pgettext("image alt text", "core.icons.bankcardcheck")),
            heading=_("eligibility.pages.start.bankcard.title"),
            details=_("eligibility.pages.start.bankcard.text"),
            links=[
                viewmodels.Button.link(
                    classes="btn-text btn-link",
                    text=_("eligibility.pages.start.bankcard.button[0].link"),
                    url=f"{reverse(ROUTE_HELP)}#payment-options",
                ),
            ],
        ),
    ]

    if verifier.requires_authentication:
        media.insert(
            0,
            dict(
                icon=viewmodels.Icon("idcardcheck", pgettext("image alt text", "core.icons.idcardcheck")),
                heading=_("eligibility.pages.start.oauth.heading"),
                details=_("eligibility.pages.start.oauth.details"),
                links=[
                    viewmodels.Button.link(
                        classes="btn-text btn-link",
                        text=_("eligibility.pages.start.oauth.link_text"),
                        url=f"{reverse(ROUTE_HELP)}#login-gov",
                    ),
                ],
                bullets=[
                    _("eligibility.pages.start.oauth.required_items[0]"),
                    _("eligibility.pages.start.oauth.required_items[1]"),
                    _("eligibility.pages.start.oauth.required_items[2]"),
                ],
            ),
        )

        if not session.logged_in(request):
            button = viewmodels.Button.login(
                text=_(verifier.auth_provider.sign_in_button_label),
                url=reverse(ROUTE_LOGIN),
            )

    else:
        media.insert(
            0,
            dict(
                icon=viewmodels.Icon("idcardcheck", pgettext("image alt text", "core.icons.idcardcheck")),
                heading=_(verifier.start_item_name),
                details=_(verifier.start_item_description),
            ),
        )

    page = viewmodels.Page(
        title=_("eligibility.pages.start.title"),
        noimage=True,
        paragraphs=[_(verifier.start_blurb)],
        button=button,
    )

    ctx = page.context_dict()
    ctx["title"] = _(verifier.start_content_title)
    ctx["media"] = media
    ctx["info_link"] = f"{reverse(ROUTE_HELP)}#about"

    return TemplateResponse(request, TEMPLATE_START, ctx)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
@decorator_from_middleware(RateLimit)
@decorator_from_middleware(VerifierSessionRequired)
def confirm(request):
    """View handler for the eligibility verification form."""

    verifier = session.verifier(request)

    page = viewmodels.Page(
        title=_(verifier.form_title),
        content_title=_(verifier.form_content_title),
        paragraphs=[_(verifier.form_blurb)],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix="", verifier=verifier),
        classes="text-lg-center",
    )

    # POST form submission, process form data
    if request.method == "POST":
        analytics.started_eligibility(request)

        form = forms.EligibilityVerificationForm(data=request.POST, verifier=verifier)

        # form was not valid, allow for correction/resubmission
        if not form.is_valid():
            if recaptcha.has_error(form):
                messages.error(request, "Recaptcha failed. Please try again.")

            page.forms = [form]
            return TemplateResponse(request, TEMPLATE_CONFIRM, page.context_dict())

        # form is valid, make Eligibility Verification request to get the verified types
        verified_types = verify.eligibility_from_api(verifier, form, session.agency(request))

        # form was not valid, allow for correction/resubmission
        if verified_types is None:
            analytics.returned_error(request, form.errors)
            page.forms = [form]
            return TemplateResponse(request, TEMPLATE_CONFIRM, page.context_dict())
        # no types were verified
        elif len(verified_types) == 0:
            return unverified(request)
        # type(s) were verified
        else:
            return verified(request, verified_types)

    # GET from an already verified user, no need to verify again
    elif session.eligible(request):
        eligibility = session.eligibility(request)
        return verified(request, [eligibility.name])

    # GET from an unverified user, see if verifier can get verified types and if not, present the form
    else:
        verified_types = verify.eligibility_from_oauth(verifier, session.oauth_claim(request), session.agency(request))
        if verified_types:
            return verified(request, verified_types)
        else:
            return TemplateResponse(request, TEMPLATE_CONFIRM, page.context_dict())


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
def verified(request, verified_types):
    """View handler for the verified eligibility page."""

    analytics.returned_success(request)

    session.update(request, eligibility_types=verified_types)

    return redirect(ROUTE_ENROLLMENT)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
@decorator_from_middleware(VerifierSessionRequired)
def unverified(request):
    """View handler for the unverified eligibility page."""

    analytics.returned_fail(request)

    # tel: link to agency phone number
    agency = session.agency(request)
    buttons = viewmodels.Button.agency_contact_links(agency)
    buttons.append(viewmodels.Button.home(request, _("core.buttons.retry")))

    verifier = session.verifier(request)

    page = viewmodels.Page(
        title=_(verifier.unverified_title),
        classes="with-agency-links",
        content_title=_(verifier.unverified_content_title),
        icon=viewmodels.Icon("idcardquestion", pgettext("image alt text", "core.icons.idcardquestion")),
        paragraphs=[_(verifier.unverified_blurb), _("eligibility.pages.unverified.p[1]")],
        buttons=buttons,
    )

    return TemplateResponse(request, TEMPLATE_UNVERIFIED, page.context_dict())
