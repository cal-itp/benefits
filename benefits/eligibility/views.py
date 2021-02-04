"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from benefits.core import middleware, session, viewmodels
from benefits.core.views import PageTemplateResponse, _index_image
from . import api, forms


@decorator_from_middleware(middleware.AgencySessionRequired)
def index(request):
    """View handler for the eligibility verification getting started screen."""

    session.update(request, eligibility_types=[], origin=reverse("eligibility:index"))

    page = viewmodels.Page(
        title="Getting started",
        content_title="Great, you’ll need two things before we get started...",
        media=[
            viewmodels.MediaItem(
                icon=viewmodels.Icon("idcardcheck", "identification card icon"),
                heading="Your California ID",
                details="Driver’s license or ID card"
            ),
            viewmodels.MediaItem(
                icon=viewmodels.Icon("paymentcardcheck", "bank card icon"),
                heading="Your bank card",
                details="A debit, credit, or Visa prepaid card"
            ),
        ],
        paragraphs=[
            "This program is currently open to those who are 65 or older. \
                Not over 65? Get in touch with your transit provider to \
                learn about other available discount programs."
        ],
        image=_index_image(),
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
        title="Confirm your age",
        content_title="Let’s see if we can confirm your age with the DMV",
        paragraphs=[
            "If you’re 65 or older, we can confirm you are eligible for a \
                senior discount when you ride transit. We don’t save your information."
        ],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix=""),
        classes="text-lg-center"
    )

    if request.method == "POST":
        form = forms.EligibilityVerificationForm(request.POST)
        response = _verify(request, form)

        if response is None:
            page.forms = [form]
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
        raise ex

    if any(types):
        return verified(request, types)
    elif any(errors):
        return api_errors(request, errors, form)
    else:
        return unverified(request)


@decorator_from_middleware(middleware.AgencySessionRequired)
def verified(request, verified_types):
    """View handler for the verified eligibility page."""

    discounts_index = reverse("discounts:index")
    session.update(request, eligibility_types=verified_types, origin=discounts_index)

    return redirect(discounts_index)


@decorator_from_middleware(middleware.AgencySessionRequired)
def api_errors(request, errors, form):
    """View handler for API error responses."""

    form_errors = [e.error for e in errors if e.status_code == 400]
    if any(form_errors):
        form.add_api_errors(form_errors)
        return

    other_errors = [e.error for e in errors if e.status_code != 400]
    if any(other_errors):
        raise Exception(api.Error(", ".join(other_errors)))


@decorator_from_middleware(middleware.AgencySessionRequired)
def unverified(request):
    """View handler for the unverified eligibility page."""

    # tel: link to agency phone number
    agency = session.agency(request)
    buttons = [viewmodels.Button.agency_phone_link(agency)]

    page = viewmodels.Page(
        title="Age not confirmed",
        content_title="We can’t confirm your age",
        icon=viewmodels.Icon("idcardquestion", "identification card icon"),
        paragraphs=[
            "You may still be eligible for a discount, but we can’t confirm \
                your age with the DMV.",
            "Reach out to your transit provider for assistance."
        ],
        buttons=buttons,
        classes="text-lg-center"
    )

    return PageTemplateResponse(request, page)
