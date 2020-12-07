"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.http import HttpResponseServerError
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from eligibility_verification.core import middleware, session, viewmodels
from eligibility_verification.core.views import PageTemplateResponse
from . import api, forms


BASE_TITLE = viewmodels.Page.from_base().title


@decorator_from_middleware(middleware.AgencySessionRequired)
def index(request):
    """View handler for the eligibility verification getting started screen."""

    session.update(request, eligibility_types=[], origin=reverse("eligibility:index"))

    page = viewmodels.Page.from_base(
        title=f"{BASE_TITLE}: Getting Started",
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
        button=viewmodels.Button.primary(
            text="Ready to continue",
            url=reverse("eligibility:verify")
        )
    )

    return PageTemplateResponse(request, page)


@decorator_from_middleware(middleware.AgencySessionRequired)
def verify(request):
    """View handler for the eligibility verification form."""

    page = viewmodels.Page(
        title=f"{BASE_TITLE}: Verify",
        content_title="Let’s see if we can verify your age with the DMV",
        paragraphs=[
            "If you’re 65 or older, we can confirm you are eligible for a \
                senior discount when you ride transit."
        ],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix=""),
        classes="text-lg-center"
    )

    if request.method == "POST":
        form = forms.EligibilityVerificationForm(request.POST)
        response = _verify(request, form)

        if response is None:
            page.form = form
            response = PageTemplateResponse(request, page)
    elif session.eligible(request):
        response = verified(request, session.eligibility(request))
    else:
        response = PageTemplateResponse(request, page)

    return response


def _verify(request, form):
    """"Helper calls the eligibility verification API to verify user input."""

    if not form.is_valid():
        return None

    sub, name = form.cleaned_data.get("sub"), form.cleaned_data.get("name")

    agency = session.agency(request)

    try:
        types, errors = api.verify(sub, name, agency)
    except Exception as ex:
        return HttpResponseServerError(ex)

    if any(types):
        return verified(request, types)
    elif any(errors):
        return api_errors(request, errors, form)
    else:
        return unverified(request)


@decorator_from_middleware(middleware.AgencySessionRequired)
def verified(request, verified_types):
    """View handler for the verified eligibility page."""

    session.update(request, eligibility_types=verified_types, origin=reverse("eligibility:verify"))

    page = viewmodels.Page(
        title=f"{BASE_TITLE}: Verified!",
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
                url="#payments"
            ),
            viewmodels.Button.link(
                classes="btn-sm",
                text="What if I don’t have a payment card?",
                url=reverse("core:payment_cards")
            )
        ]
    )

    return PageTemplateResponse(request, page)


@decorator_from_middleware(middleware.AgencySessionRequired)
def api_errors(request, errors, form):
    """View handler for API error responses."""

    form_errors = [e.error for e in errors if e.status_code == 400]
    if any(form_errors):
        form.add_api_errors(form_errors)
        return None

    other_errors = [e.error for e in errors if e.status_code != 400]
    if any(other_errors):
        return HttpResponseServerError(api.Error(", ".join(other_errors)))


@decorator_from_middleware(middleware.AgencySessionRequired)
def unverified(request):
    """View handler for the unverified eligibility page."""

    # tel: link to agency phone number
    agency = session.agency(request)
    buttons = [viewmodels.Button.agency_phone_link(agency)]

    page = viewmodels.Page(
        title=f"{BASE_TITLE}: Age not verified",
        content_title="We can’t verify your age",
        icon=viewmodels.Icon("idcardquestion", "identification card icon"),
        paragraphs=[
            "You may still be eligible for a discount but we can’t verify \
                your age with the DMV.",
            "Reach out to your transit provider for assistance."
        ],
        buttons=buttons,
        classes="text-lg-center"
    )

    return PageTemplateResponse(request, page)
