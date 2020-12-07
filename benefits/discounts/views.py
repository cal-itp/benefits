"""
The discounts application: view definitions for the discounts association flow.
"""
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from benefits.core import middleware, viewmodels
from . import api, forms


@decorator_from_middleware(middleware.AgencySessionRequired)
def index(request):
    """View handler for the discounts landing page."""

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
        buttons=[
            viewmodels.Button.primary(
                text="Continue to our payment partner",
                url="#"
            ),
            viewmodels.Button.link(
                classes="btn-sm",
                text="What if I don’t have a payment card?",
                url=reverse("core:payment_cards")
            )
        ]
    )

    return TemplateResponse(request, "discounts/index.html", page.context_dict())


def success(request):
    """View handler for the final success page."""

    page = viewmodels.Page(
        title="Success!",
        content_title="Success!",
        icon=viewmodels.Icon("paymentcardcheck", "Payment card verified icon")
    )

    return TemplateResponse(request, "discounts/success.html", page.context_dict())
