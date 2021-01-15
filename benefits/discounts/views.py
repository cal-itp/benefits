"""
The discounts application: view definitions for the discounts association flow.
"""
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from benefits.core import middleware, session, viewmodels
from . import api, forms


def _check_access_token(request, agency):
    """
    Ensure the request's session is configured with an access token.
    Raise an exception if an access token cannot be obtained.
    """
    if not session.valid_token(request):
        response = api.Client(agency=agency).access_token()
        if isinstance(response, api.AccessTokenResponse) and response.is_success():
            session.update(request, token=response.access_token, token_exp=response.expiry)
        else:
            raise Exception(response.error)


def _index(request):
    """Helper handles GET requests to discounts index."""
    agency = session.agency(request)

    _check_access_token(request, agency)

    tokenize_button = "tokenize_card"

    page = viewmodels.Page(
        title="Eligibility Verified!",
        content_title="Great! You’re eligible for a senior discount!",
        icon=viewmodels.Icon("idcardcheck", "identification card icon"),
        paragraphs=[
            "Next, we need to attach your discount to your payment card so \
                when you pay with that card, you always get your discount.",
            "Use a credit, debit, or prepaid card."
        ],
        classes="text-lg-center",
        form=forms.CardTokenForm(auto_id=True, label_suffix=""),
        buttons=[
            viewmodels.Button.primary(
                text="Continue to our payment partner",
                id=tokenize_button,
                url=f"#{tokenize_button}"
            ),
            viewmodels.Button.link(
                classes="btn-sm",
                text="What if I don’t have a payment card?",
                url=reverse("core:payment_cards")
            )
        ]
    )
    context = page.context_dict()

    # add agency details
    agency_vm = viewmodels.TransitAgency(agency)
    context.update(agency_vm.context_dict())

    # and discount provider details
    provider_vm = viewmodels.DiscountProvider(
        model=agency.discount_provider,
        access_token=session.token(request),
        element_id=f"#{tokenize_button}"
    )
    context.update(provider_vm.context_dict())

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
    form = forms.CardTokenForm(request.POST)
    if not form.is_valid():
        raise Exception("[Card token]: ")
    pass


def success(request):
    """View handler for the final success page."""

    page = viewmodels.Page(
        title="Success!",
        content_title="Success!",
        icon=viewmodels.Icon("paymentcardcheck", "Payment card verified icon")
    )

    return TemplateResponse(request, "discounts/success.html", page.context_dict())
