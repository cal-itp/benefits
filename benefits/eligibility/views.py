"""
The eligibility application: view definitions for the eligibility verification flow.
"""
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.utils.translation import pgettext, gettext as _

from benefits.core import middleware, recaptcha, session, viewmodels
from benefits.core.views import PageTemplateResponse, _index_image
from . import analytics, api, forms


@decorator_from_middleware(middleware.AgencySessionRequired)
def index(request):
    """View handler for the eligibility verification getting started screen."""

    session.update(request, eligibility_types=[], origin=reverse("eligibility:index"))

    page = viewmodels.Page(
        title=_("eligibility.index.title"),
        content_title=_("eligibility.index.content_title"),
        media=[
            viewmodels.MediaItem(
                icon=viewmodels.Icon("idcardcheck", pgettext("image alt text", "core.icons.idcardcheck")),
                heading=_("eligibility.index.item1.title"),
                details=_("eligibility.index.item1.text"),
            ),
            viewmodels.MediaItem(
                icon=viewmodels.Icon("bankcardcheck", pgettext("image alt text", "core.icons.bankcardcheck")),
                heading=_("eligibility.index.item2.title"),
                details=_("eligibility.index.item2.text"),
            ),
        ],
        paragraphs=[_("eligibility.index.p1")],
        image=_index_image(),
        button=viewmodels.Button.primary(text=_("eligibility.index.button"), url=reverse("eligibility:confirm")),
    )

    return PageTemplateResponse(request, page)


@decorator_from_middleware(middleware.AgencySessionRequired)
@decorator_from_middleware(middleware.RateLimit)
def confirm(request):
    """View handler for the eligibility verification form."""

    page = viewmodels.Page(
        title=_("eligibility.confirm.title"),
        content_title=_("eligibility.confirm.content_title"),
        paragraphs=[_("eligibility.confirm.p1")],
        form=forms.EligibilityVerificationForm(auto_id=True, label_suffix=""),
        classes="text-lg-center",
    )

    if request.method == "POST":
        analytics.started_eligibility(request)

        form = forms.EligibilityVerificationForm(request.POST)
        response = _verify(request, form)

        if response is None:
            # form was not valid, allow for correction/resubmission
            analytics.returned_error(request, form.errors)
            page.forms = [form]
            response = PageTemplateResponse(request, page)
    elif session.eligible(request):
        eligibility = session.eligibility(request)
        response = verified(request, [eligibility.name])
    else:
        response = PageTemplateResponse(request, page)

    return response


def _verify(request, form):
    """Helper calls the eligibility verification API with user input."""

    if not form.is_valid():
        if recaptcha.has_error(form):
            messages.error(request, "Recaptcha failed. Please try again.")
        return None

    sub, name = form.cleaned_data.get("sub"), form.cleaned_data.get("name")

    agency = session.agency(request)
    client = api.Client(agency)

    response = client.verify(sub, name)

    if response.error and any(response.error):
        form.add_api_errors(response.error)
        return None
    elif any(response.eligibility):
        return verified(request, response.eligibility)
    else:
        return unverified(request)


@decorator_from_middleware(middleware.AgencySessionRequired)
def verified(request, verified_types):
    """View handler for the verified eligibility page."""

    analytics.returned_success(request)

    enrollment_index = reverse("enrollment:index")
    session.update(request, eligibility_types=verified_types, origin=enrollment_index)

    return redirect(enrollment_index)


@decorator_from_middleware(middleware.AgencySessionRequired)
def unverified(request):
    """View handler for the unverified eligibility page."""

    analytics.returned_fail(request)

    # tel: link to agency phone number
    agency = session.agency(request)
    buttons = viewmodels.Button.agency_contact_links(agency)

    page = viewmodels.Page(
        title=_("eligibility.unverified.title"),
        content_title=_("eligibility.unverified.content_title"),
        icon=viewmodels.Icon("idcardquestion", pgettext("image alt text", "core.icons.idcardquestion")),
        paragraphs=[_("eligibility.unverified.p1"), _("eligibility.unverified.p2")],
        buttons=buttons,
        classes="text-lg-center",
    )

    return PageTemplateResponse(request, page)
