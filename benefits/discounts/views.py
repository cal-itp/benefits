"""
The discounts application: view definitions for the discounts association flow.
"""
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from benefits.core import middleware, session, viewmodels
from benefits.core.views import PageTemplateResponse
from . import api, forms


def _check_access_token(request, agency):
    """
    Ensure the request's session is configured with an access token.
    Raise an exception if an access token cannot be obtained.
    """
    if not session.valid_token(request):
        response = api.AccessTokenClient(agency=agency).get()
        if isinstance(response, api.AccessTokenResponse) and response.is_success():
            session.update(request, token=response.access_token, token_exp=response.expiry)
        else:
            raise Exception(response.error)


def _index(request):
    """Helper handles GET requests to discounts index."""
    agency = session.agency(request)

    _check_access_token(request, agency)

    tokenize_button = "tokenize_card"
    tokenize_retry_form = forms.CardTokenizeFailForm("discounts:retry")
    tokenize_success_form = forms.CardTokenizeSuccessForm(auto_id=True, label_suffix="")

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
        forms=[tokenize_retry_form, tokenize_success_form],
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
        element_id=f"#{tokenize_button}",
        color="#046b99",
        name=f"{agency.long_name} partnered with {agency.discount_provider.name}"
    )
    context.update(provider_vm.context_dict())

    # the tokenize form URLs are injected to page-generated Javascript
    context.update({"forms": {
        "tokenize_retry": reverse(tokenize_retry_form.action_url),
        "tokenize_success": reverse(tokenize_success_form.action_url)
    }})

    return TemplateResponse(request, "discounts/index.html", context)


def _associate_discount(request):
    """Helper calls the discount APIs."""
    form = forms.CardTokenForm(request.POST)
    if not form.is_valid():
        raise Exception("Invalid card token form.")
    card_token = form.cleaned_data.get("card_token")

    eligibility = session.eligibility(request)
    if len(eligibility) == 1:
        eligibility = eligibility[0]
    else:
        raise Exception("Session contains more than one eligibility")

    agency = session.agency(request)

    response = api.CustomerClient(agency=agency).create_or_update(card_token)
    if not isinstance(response, api.CustomerResponse) and response.is_success():
        raise Exception(response.error)
    customer_id = response.id

    response = api.GroupClient(agency=agency).enroll_customer(customer_id, eligibility.group_id)
    if not isinstance(response, api.GroupResponse) and response.is_success():
        raise Exception(response.error)

    if response.updated_customer_id == customer_id:
        return success(request)
    else:
        raise Exception("Updated customer_id does not match enrolled customer_id")


@decorator_from_middleware(middleware.AgencySessionRequired)
def index(request):
    """View handler for the discounts landing page."""
    if request.method == "POST":
        response = _associate_discount(request)
    else:
        response = _index(request)

    return response


@decorator_from_middleware(middleware.AgencySessionRequired)
def retry(request):
    """View handler for a recoverable failure condition."""
    if request.method == "POST":
        form = forms.CardTokenizeFailForm(request.POST)
        if form.is_valid():
            agency = session.agency(request)
            page = viewmodels.Page(
                title="We couldn’t connect your payment card",
                icon=viewmodels.Icon("paymentcardquestion", "Payment card question icon"),
                content_title="We couldn’t connect your payment card",
                paragraphs=["You can try again or reach out to your transit provider for assistance."],
                buttons=[
                    viewmodels.Button.agency_phone_link(agency),
                    viewmodels.Button.primary(text="Try again", url=session.origin(request))
                ]
            )
            return PageTemplateResponse(request, page)
        else:
            raise Exception("Invalid retry submission.")
    else:
        raise ValueError("This view method only supports POST.")


def success(request):
    """View handler for the final success page."""

    page = viewmodels.Page(
        title="Success!",
        content_title="Success!",
        icon=viewmodels.Icon("paymentcardcheck", "Payment card verified icon")
    )

    return TemplateResponse(request, "discounts/success.html", page.context_dict())
