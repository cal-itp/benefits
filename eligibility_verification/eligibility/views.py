"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.http import HttpResponseServerError
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from eligibility_verification.core import middleware, models, viewmodels
from eligibility_verification.settings import DEBUG
from . import api, forms


@decorator_from_middleware(middleware.AgencyRequiredMiddleware)
def index(request):
    """View handler for the eligibility verification getting started screen."""

    page = viewmodels.page_from_base(
        title=f"{viewmodels.BASE_PAGE.title}: Getting Started",
        content_title="Great, you’ll need two things before we get started...",
        media=[
            viewmodels.MediaItem(
                icon=viewmodels.Icon("idcardcheck", "identification card icon"),
                heading="Your California ID",
                details="Driver License or ID card"
            ),
            viewmodels.MediaItem(
                icon=viewmodels.Icon("paymentcardcheck", "payment card icon"),
                heading="Your payment card",
                details="A debit, credit, or prepaid card"
            ),
        ],
        paragraphs=[
            "This program is currently open to those who are 65 or older. \
                Not over 65? Get in touch with your transit provider to \
                learn about available discount programs."
        ],
        button=viewmodels.Button(
            classes="btn-primary",
            text="Ready to continue",
            url=reverse("eligibility:verify")
        )
    )

    return TemplateResponse(request, "core/page.html", page.context_dict())


@decorator_from_middleware(middleware.AgencyRequiredMiddleware)
def verify(request):
    """View handler for the eligibility verification form."""

    page = viewmodels.Page(
        title=f"{viewmodels.BASE_PAGE.title}: Verify",
        content_title="Let’s see if we can verify your age with the DMV",
        paragraphs=[
            "If you’re 65 or older, we can confirm you are eligible for a \
                senior discount when you ride transit."
        ],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix="")
    )

    context = page.context_dict()

    if request.method == "POST":
        form = forms.EligibilityVerificationForm(request.POST)
        response = _verify(request, form)

        if response is None:
            page.form = form
            response = TemplateResponse(request, "core/page.html", context)
    else:
        response = TemplateResponse(request, "core/page.html", context)

    return response


def _verify(request, form):
    """"Helper calls the eligibility verification API to verify user input."""

    if not form.is_valid():
        return None

    sub, name = form.cleaned_data.get("card"), form.cleaned_data.get("last_name")

    if not all((sub, name)):
        raise ValueError("Missing form data")

    agency = models.TransitAgency.by_id(request.session["agency"])

    try:
        types, errors = api.verify(sub, name, agency)
    except Exception as ex:
        return HttpResponseServerError(ex)

    if any(types):
        debug = {"eligibility": types} if DEBUG else None
        return verified(request, types, debug)
    else:
        debug = {"errors": errors} if DEBUG else None
        return unverified(request, errors, debug)


@decorator_from_middleware(middleware.AgencyRequiredMiddleware)
def verified(request, verified_types, debug=None):
    """View handler for the verified eligibility page."""

    # keep a ref to the verified types in session
    request.session["eligibility"] = verified_types

    page = viewmodels.Page(
        title=f"{viewmodels.BASE_PAGE.title}: Verified!",
        content_title="Great! You’re eligible for a senior discount!",
        icon=viewmodels.Icon("idcardcheck", "identification card icon"),
        paragraphs=[
            "Next, we need to attach your discount to your payment card so \
                when you pay with that card, you always get your discount.",
            "Use a credit, debit, or prepaid card."
        ],
        buttons=[
            viewmodels.Button(
                classes="btn-primary",
                text="Continue to our payment partner",
                url="#payments"
            ),
            viewmodels.Button(
                classes="btn-link btn-sm",
                text="What if I don’t have a payment card?",
                url="#payments/no-card"
            )
        ],
        debug=debug
    )

    return TemplateResponse(request, "core/page.html", page.context_dict())


@decorator_from_middleware(middleware.AgencyRequiredMiddleware)
def unverified(request, errors, debug=None):
    """View handler for the unverified eligibility page."""

    # query all active agencies
    agencies = models.TransitAgency.all_active()

    # generate buttons with phone number links
    buttons = [
        viewmodels.Button(
            classes="btn-link text-left pl-0 pt-0 border-left-0",
            text=a.phone,
            url=f"tel:{a.phone}",
            label=f"{a.long_name}:")
        for a in agencies
    ]

    page = viewmodels.Page(
        title=f"{viewmodels.BASE_PAGE.title}: Age not verified",
        content_title="We can’t verify your age",
        icon=viewmodels.Icon("idcardquestion", "identification card icon"),
        paragraphs=[
            "You may still be eligible for a discount but we can’t verify \
                your age with the DMV.",
            "Reach out to your transit provider for assistance."
        ],
        buttons=buttons,
        debug=debug
    )

    return TemplateResponse(request, "core/page.html", page.context_dict())
