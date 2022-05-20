"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.utils.translation import pgettext, gettext as _

from eligibility_api.client import Client

from benefits.core import recaptcha, session, viewmodels
from benefits.core.middleware import AgencySessionRequired, LoginRequired, RateLimit, VerifierSessionRequired
from benefits.core.models import EligibilityVerifier
from benefits.core.views import PageTemplateResponse
from . import analytics, forms


@decorator_from_middleware(AgencySessionRequired)
def index(request):
    """View handler for the eligibility verifier selection form."""

    session.update(request, eligibility_types=[], origin=reverse("eligibility:index"))
    agency = session.agency(request)

    eligibility_start = reverse("eligibility:start")

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
            response = PageTemplateResponse(request, page)
    else:
        if agency.eligibility_verifiers.count() == 1:
            verifier = agency.eligibility_verifiers.first()
            session.update(request, verifier=verifier)
            response = redirect(eligibility_start)
        else:
            response = PageTemplateResponse(request, page)

    return response


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(VerifierSessionRequired)
def start(request):
    """View handler for the eligibility verification getting started screen."""

    session.update(request, eligibility_types=[], origin=reverse("eligibility:start"))
    verifier = session.verifier(request)

    button = viewmodels.Button.primary(text=_("eligibility.buttons.continue"), url=reverse("eligibility:confirm"))

    payment_options_link = f"{reverse('core:help')}#payment-options"
    media = [
        dict(
            icon=viewmodels.Icon("idcardcheck", pgettext("image alt text", "core.icons.idcardcheck")),
            heading=_(verifier.start_item_name),
            details=_(verifier.start_item_description),
        ),
        dict(
            icon=viewmodels.Icon("bankcardcheck", pgettext("image alt text", "core.icons.bankcardcheck")),
            heading=_("eligibility.pages.start.bankcard.title"),
            details=_("eligibility.pages.start.bankcard.text"),
            links=[
                viewmodels.Button.link(
                    classes="btn-text btn-link",
                    text=_("eligibility.pages.start.bankcard.button[0].link"),
                    url=payment_options_link,
                ),
                viewmodels.Button.link(
                    classes="btn-text btn-link",
                    text=_("eligibility.pages.start.bankcard.button[1].link"),
                    url=payment_options_link,
                ),
            ],
        ),
    ]

    if verifier.requires_authentication:
        if settings.OAUTH_CLIENT_NAME is None:
            raise Exception("EligibilityVerifier requires authentication, but OAUTH_CLIENT_NAME is None")

        oauth_help_link = f"{reverse('core:help')}#login-gov"

        media.insert(
            0,
            dict(
                icon=viewmodels.Icon("idscreencheck", pgettext("image alt text", "core.icons.idscreencheck")),
                heading=_("eligibility.pages.start.oauth.heading"),
                details=_("eligibility.pages.start.oauth.details"),
                links=[
                    viewmodels.Button.link(
                        classes="btn-text btn-link",
                        text=_("eligibility.pages.start.oauth.link_text"),
                        url=oauth_help_link,
                        rel="noopener noreferrer",
                    )
                ],
            ),
        )

        if not session.logged_in(request):
            button = viewmodels.Button.login(
                label=_(verifier.auth_provider.sign_in_button_label),
                text="",
                url=reverse("oauth:login"),
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

    return TemplateResponse(request, "eligibility/start.html", ctx)


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

    if request.method == "POST":
        analytics.started_eligibility(request)

        form = forms.EligibilityVerificationForm(data=request.POST, verifier=verifier)
        response = _verify(request, form)

        if response is None:
            # form was not valid, allow for correction/resubmission
            analytics.returned_error(request, form.errors)
            page.forms = [form]
            response = TemplateResponse(request, "eligibility/confirm.html", page.context_dict())
    elif session.eligible(request):
        eligibility = session.eligibility(request)
        response = verified(request, [eligibility.name])
    else:
        response = TemplateResponse(request, "eligibility/confirm.html", page.context_dict())

    return response


def _verify(request, form):
    """Helper calls the eligibility verification API with user input."""

    if not form.is_valid():
        if recaptcha.has_error(form):
            messages.error(request, "Recaptcha failed. Please try again.")
        return None

    sub, name = form.cleaned_data.get("sub"), form.cleaned_data.get("name")

    agency = session.agency(request)
    verifier = session.verifier(request)

    client = Client(
        api_url=verifier.api_url,
        api_auth_header=verifier.api_auth_header,
        api_auth_key=verifier.api_auth_key,
        issuer=settings.ALLOWED_HOSTS[0],
        agency_identifier=agency.agency_id,
        jws_signing_alg=agency.jws_signing_alg,
        client_private_jwk=agency.private_jwk,
        jwe_encryption_alg=verifier.jwe_encryption_alg,
        jwe_cek_enc=verifier.jwe_cek_enc,
        server_public_jwk=verifier.public_jwk,
    )

    # get the eligibility type names
    types = list(map(lambda t: t.name, agency.types_to_verify(verifier)))

    response = client.verify(sub, name, types)

    if response.error and any(response.error):
        form.add_api_errors(response.error)
        return None
    elif any(response.eligibility):
        return verified(request, response.eligibility)
    else:
        return unverified(request)


@decorator_from_middleware(AgencySessionRequired)
@decorator_from_middleware(LoginRequired)
def verified(request, verified_types):
    """View handler for the verified eligibility page."""

    analytics.returned_success(request)

    session.update(request, eligibility_types=verified_types)

    return redirect("enrollment:index")


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

    return TemplateResponse(request, "eligibility/unverified.html", page.context_dict())
