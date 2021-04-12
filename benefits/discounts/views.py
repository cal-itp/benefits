"""
The discounts application: view definitions for the discounts association flow.
"""
import logging

from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.utils.translation import pgettext, ugettext as _

from benefits.core import middleware, models, session, viewmodels
from benefits.core.views import PageTemplateResponse
from . import api, forms


logger = logging.getLogger(__name__)


def _check_access_token(request, agency):
    """
    Ensure the request's session is configured with an access token.
    """
    if not session.valid_token(request):
        response = api.AccessTokenClient(agency).get()
        session.update(request, token=response.access_token, token_exp=response.expiry)


def _index(request):
    """Helper handles GET requests to discounts index."""
    agency = session.agency(request)

    _check_access_token(request, agency)

    tokenize_button = "tokenize_card"
    tokenize_retry_form = forms.CardTokenizeFailForm("discounts:retry")
    tokenize_success_form = forms.CardTokenizeSuccessForm(auto_id=True, label_suffix="")

    page = viewmodels.Page(
        title=_("discounts.index.title"),
        content_title=_("discounts.index.content_title"),
        icon=viewmodels.Icon("idcardcheck", pgettext("image alt text", "core.icons.idcardcheck")),
        paragraphs=[_("discounts.index.p1"), _("discounts.index.p2")],
        classes="text-lg-center",
        forms=[tokenize_retry_form, tokenize_success_form],
        buttons=[
            viewmodels.Button.primary(
                text=_("discounts.buttons.paymentpartner"), id=tokenize_button, url=f"#{tokenize_button}"
            ),
            viewmodels.Button.link(
                classes="btn-sm", text=_("discounts.buttons.paymentoptions"), url=reverse("core:payment_options")
            ),
        ],
    )
    context = {}
    context.update(page.context_dict())

    # add agency details
    agency_vm = viewmodels.TransitAgency(agency)
    context.update(agency_vm.context_dict())

    # and discount provider details
    provider_vm = viewmodels.DiscountProvider(
        model=agency.discount_provider,
        access_token=session.token(request),
        element_id=f"#{tokenize_button}",
        color="#046b99",
        name=f"{agency.long_name} {_('partnered with')} {agency.discount_provider.name}",
    )
    context.update(provider_vm.context_dict())
    logger.info(f"card_tokenize_url: {context['provider'].card_tokenize_url}")

    # the tokenize form URLs are injected to page-generated Javascript
    context["forms"] = {
        "tokenize_retry": reverse(tokenize_retry_form.action_url),
        "tokenize_success": reverse(tokenize_success_form.action_url),
    }

    return TemplateResponse(request, "discounts/index.html", context)


@decorator_from_middleware(middleware.AgencySessionRequired)
def index(request):
    """View handler for the discounts landing page."""
    if request.method == "POST":
        response = _associate_discount(request)
    else:
        response = _index(request)

    return response


def _associate_discount(request):
    """Helper calls the discount APIs."""
    logger.debug("Read tokenized card")
    form = forms.CardTokenizeSuccessForm(request.POST)
    if not form.is_valid():
        raise Exception("Invalid card token form")
    card_token = form.cleaned_data.get("card_token")

    eligibility = session.eligibility(request)
    if len(eligibility) > 0:
        eligibility = eligibility[0]
        if len(eligibility) == 1:
            logger.debug(f"Session contains 1 {models.EligibilityType.__name__}")
        else:
            logger.debug(f"Session contains ({len(eligibility)}) {models.EligibilityType.__name__}s")
    else:
        raise Exception("Session contains no eligibility information")

    agency = session.agency(request)

    logger.debug("Call customer API")
    response = api.CustomerClient(agency).get(card_token)
    customer_id = response.id

    logger.debug("Call group API")
    eligibility = models.EligibilityType.by_name(eligibility)
    response = api.GroupClient(agency).enroll_customer(customer_id, eligibility.group_id)
    if response.updated_customer_id == customer_id:
        return success(request)
    else:
        raise Exception("Updated customer_id does not match enrolled customer_id")


@decorator_from_middleware(middleware.AgencySessionRequired)
def retry(request):
    """View handler for a recoverable failure condition."""
    if request.method == "POST":
        form = forms.CardTokenizeFailForm(request.POST)
        if form.is_valid():
            agency = session.agency(request)
            page = viewmodels.Page(
                title=_("discounts.retry.title"),
                icon=viewmodels.Icon("bankcardquestion", pgettext("image alt text", "core.icons.bankcardquestion")),
                content_title=_("discounts.retry.title"),
                paragraphs=[_("discounts.retry.p1")],
                buttons=[
                    viewmodels.Button.agency_phone_link(agency),
                    viewmodels.Button.primary(text=_("discounts.retry.button"), url=session.origin(request)),
                ],
            )
            return PageTemplateResponse(request, page)
        else:
            raise Exception("Invalid retry submission.")
    else:
        raise Exception("This view method only supports POST.")


@middleware.pageview_decorator
def success(request):
    """View handler for the final success page."""

    request.path = "/discounts/success"

    page = viewmodels.Page(
        title=_("discounts.success.title"),
        icon=viewmodels.Icon("bankcardcheck", pgettext("image alt text", "core.icons.bankcardcheck")),
        content_title=_("discounts.success.title"),
        paragraphs=[_("discounts.success.p1"), _("discounts.success.p2")],
    )

    return TemplateResponse(request, "discounts/success.html", page.context_dict())
