"""
The enrollment application: view definitions for the benefits enrollment flow.
"""
import logging

from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.decorators import decorator_from_middleware
from django.utils.translation import pgettext, gettext as _

from benefits.core import models, session, viewmodels
from benefits.core.middleware import EligibleSessionRequired, VerifierSessionRequired, pageview_decorator
from benefits.core.views import ROUTE_HELP, ROUTE_LOGGED_OUT
from . import analytics, api, forms


ROUTE_INDEX = "enrollment:index"
ROUTE_RETRY = "enrollment:retry"
ROUTE_SUCCESS = "enrollment:success"
ROUTE_TOKEN = "enrollment:token"

TEMPLATE_INDEX = "enrollment/index.html"
TEMPLATE_RETRY = "enrollment/retry.html"
TEMPLATE_SUCCESS = "enrollment/success.html"


logger = logging.getLogger(__name__)


@decorator_from_middleware(EligibleSessionRequired)
def token(request):
    """View handler for the enrollment auth token."""
    if not session.enrollment_token_valid(request):
        agency = session.agency(request)
        response = api.Client(agency).access_token()
        session.update(request, enrollment_token=response.access_token, enrollment_token_exp=response.expiry)

    data = {"token": session.enrollment_token(request)}

    return JsonResponse(data)


@decorator_from_middleware(EligibleSessionRequired)
def index(request):
    """View handler for the enrollment landing page."""
    session.update(request, origin=reverse(ROUTE_INDEX))

    agency = session.agency(request)
    verifier = session.verifier(request)

    # POST back after payment processor form, process card token
    if request.method == "POST":
        form = forms.CardTokenizeSuccessForm(request.POST)
        if not form.is_valid():
            raise Exception("Invalid card token form")

        eligibility = session.eligibility(request)
        logger.debug(f"Session contains an {models.EligibilityType.__name__}")

        logger.debug("Read tokenized card")
        card_token = form.cleaned_data.get("card_token")

        response = api.Client(agency).enroll(card_token, eligibility.group_id)
        if response.success:
            analytics.returned_success(request, eligibility.group_id)
            return success(request)
        else:
            analytics.returned_error(request, response.message)
            raise Exception(response.message)

    # GET enrollment index, with button to initiate payment processor connection
    else:
        tokenize_button = "tokenize_card"
        tokenize_retry_form = forms.CardTokenizeFailForm(ROUTE_RETRY)
        tokenize_success_form = forms.CardTokenizeSuccessForm(auto_id=True, label_suffix="")

        media = []

        if verifier.eligibility_confirmed_item_heading or verifier.eligibility_confirmed_item_details:
            heading = _(verifier.eligibility_confirmed_item_heading) if verifier.eligibility_confirmed_item_heading else None
            details = (
                _(verifier.eligibility_confirmed_item_details) % {"transit_agency_short_name": agency.short_name}
                if verifier.eligibility_confirmed_item_details
                else None
            )
            confirmed_eligibility_item = viewmodels.MediaItem(
                icon=viewmodels.Icon("happybus", pgettext("image alt text", "core.icons.happybus")),
                heading=heading,
                details=details,
            )
            media.append(confirmed_eligibility_item)

        help_link = reverse(ROUTE_HELP)
        link_card_item = viewmodels.MediaItem(
            icon=viewmodels.Icon("bankcardcheck", pgettext("image alt text", "core.icons.bankcardcheck")),
            heading=_("enrollment.pages.index.link_card_item.heading"),
            details=[
                format_html(_("enrollment.pages.index.link_card_item.p[0]%(link)s") % {"link": f"{help_link}#littlepay"}),
                _("enrollment.pages.index.link_card_item.p[1]"),
            ],
        )
        media.append(link_card_item)

        page = viewmodels.Page(
            title=_("enrollment.pages.index.title"),
            headline=_("enrollment.pages.index.headline"),
            forms=[tokenize_retry_form, tokenize_success_form],
            buttons=[
                viewmodels.Button.primary(
                    text=_("enrollment.buttons.payment_partner"), id=tokenize_button, url=f"#{tokenize_button}"
                ),
            ],
        )
        context = {"media": media}
        context.update(page.context_dict())

        # add agency details
        agency_vm = viewmodels.TransitAgency(agency)
        context.update(agency_vm.context_dict())

        # and payment processor details
        processor_vm = viewmodels.PaymentProcessor(
            model=agency.payment_processor,
            access_token_url=reverse(ROUTE_TOKEN),
            element_id=f"#{tokenize_button}",
            color="#046b99",
            name=f"{agency.long_name} {_('partnered with')} {agency.payment_processor.name}",
        )
        context.update(processor_vm.context_dict())
        logger.warning(f"card_tokenize_url: {context['payment_processor'].card_tokenize_url}")

        # the tokenize form URLs are injected to page-generated Javascript
        context["forms"] = {
            "tokenize_retry": reverse(tokenize_retry_form.action_url),
            "tokenize_success": reverse(tokenize_success_form.action_url),
        }

        return TemplateResponse(request, TEMPLATE_INDEX, context)


@decorator_from_middleware(EligibleSessionRequired)
def retry(request):
    """View handler for a recoverable failure condition."""
    if request.method == "POST":
        analytics.returned_retry(request)
        form = forms.CardTokenizeFailForm(request.POST)
        if form.is_valid():
            agency = session.agency(request)
            page = viewmodels.Page(
                title=_("enrollment.pages.retry.title"),
                icon=viewmodels.Icon("bankcardquestion", pgettext("image alt text", "core.icons.bankcardquestion")),
                headline=_("enrollment.pages.retry.title"),
                paragraphs=[_("enrollment.pages.retry.p[0]")],
                buttons=viewmodels.Button.agency_contact_links(agency),
            )
            page.buttons.append(viewmodels.Button.primary(text=_("core.buttons.retry"), url=session.origin(request)))
            return TemplateResponse(request, TEMPLATE_RETRY, page.context_dict())
        else:
            analytics.returned_error(request, "Invalid retry submission.")
            raise Exception("Invalid retry submission.")
    else:
        analytics.returned_error(request, "This view method only supports POST.")
        raise Exception("This view method only supports POST.")


@pageview_decorator
@decorator_from_middleware(VerifierSessionRequired)
def success(request):
    """View handler for the final success page."""
    request.path = "/enrollment/success"
    session.update(request, origin=reverse(ROUTE_SUCCESS))

    verifier = session.verifier(request)

    page = viewmodels.Page(title=_("enrollment.pages.success.title"), headline=_("enrollment.pages.success.headline"))

    if verifier.is_auth_required and session.logged_in(request):
        # overwrite origin for a logged in user
        # if they click the logout button, they are taken to the new route
        session.update(request, origin=reverse(ROUTE_LOGGED_OUT))
        page.buttons = [viewmodels.Button.logout()]

    success_item = viewmodels.MediaItem(
        icon=viewmodels.Icon("happybus", pgettext("image alt text", "core.icons.happybus")),
        details=[
            _(verifier.enrollment_success_confirm_item_details),
            format_html(_("enrollment.pages.success.helplink%(link)s") % {"link": f"{reverse(ROUTE_HELP)}"}),
        ],
    )
    media = [success_item]

    if verifier.enrollment_success_expiry_item_heading or verifier.enrollment_success_expiry_item_details:
        heading = (
            _(verifier.enrollment_success_expiry_item_heading) if verifier.enrollment_success_expiry_item_heading else None
        )
        details = (
            _(verifier.enrollment_success_expiry_item_details) if verifier.enrollment_success_expiry_item_details else None
        )
        expiry_item = viewmodels.MediaItem(
            icon=viewmodels.Icon("calendarcheck", pgettext("image alt text", "core.icons.calendarcheck")),
            heading=heading,
            details=details,
        )
        media.insert(0, expiry_item)

    context = {"media": media}
    context.update(page.context_dict())

    return TemplateResponse(request, TEMPLATE_SUCCESS, context)
