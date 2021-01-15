"""
The core application: view definition for the root of the webapp.
"""
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse

from . import models, session, viewmodels


def PageTemplateResponse(request, page_vm):
    """Helper returns a TemplateResponse using the common page template."""
    return TemplateResponse(request, "core/page.html", page_vm.context_dict())


def _index_url():
    """Helper computes the index url path."""
    return reverse("core:index")


def index(request):
    """View handler for the main entry page."""
    session.reset(request)

    # query all active agencies
    agencies = models.TransitAgency.all_active()

    # generate a button to the landing page for each
    buttons = [
        viewmodels.Button.outline_primary(text=a.short_name, url=a.index_url)
        for a in agencies
    ]
    buttons[0].classes.append("mt-3")
    buttons[0].label = "Choose your transit provider"

    page = viewmodels.Page.from_base(buttons=buttons, classes="home")

    return PageTemplateResponse(request, page)


def agency_index(request, agency):
    """View handler for an agency entry page."""
    session.reset(request)
    session.update(request, agency=agency, origin=agency.index_url)

    page = viewmodels.Page.from_base(
        button=viewmodels.Button.primary(
            text="Let’s do it!",
            url=reverse("eligibility:index")
        ),
        classes="home"
    )

    return PageTemplateResponse(request, page)


def help(request):
    """View handler for the help page."""

    if session.active_agency(request):
        agency = session.agency(request)
        buttons = [viewmodels.Button.agency_phone_link(agency)]
    else:
        buttons = [
            viewmodels.Button.agency_phone_link(a)
            for a in models.TransitAgency.all_active()
        ]

    buttons.append(viewmodels.Button.home(request, "Go back"))

    page = viewmodels.Page(
        title="Help",
        content_title="Help",
        paragraphs=[
            "Cal-ITP is a new program serving all Californians. \
                The best way to get support if you hit a problem on this site \
                is to reach out to customer service for your local transit provider."
        ],
        buttons=buttons,
        classes="text-lg-center",
    )

    return PageTemplateResponse(request, page)


def payment_cards(request):
    """View handler for the 'What if I don't have a payment card?' page."""
    page = viewmodels.Page(
        title="Payment Cards",
        icon=viewmodels.Icon("paymentcardcheck", "payment card icon"),
        content_title="What if I don't have a payment card?",
        buttons=viewmodels.Button.home(request, text="Go back")
    )
    return TemplateResponse(request, "core/payment-cards.html", page.context_dict())


def privacy(request):
    """View handler for the privacy policy page."""
    page = viewmodels.Page(title="Privacy Policy")
    return TemplateResponse(request, "core/privacy.html", page.context_dict())


def bad_request(request, exception, template_name="400.html"):
    """View handler for HTTP 400 Bad Request responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=_index_url())

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.error(button=home)
    t = loader.get_template(template_name)

    return HttpResponseBadRequest(t.render(page.context_dict()))


def page_not_found(request, exception, template_name="404.html"):
    """View handler for HTTP 404 Not Found responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=_index_url())

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.not_found(button=home, path=request.path)
    t = loader.get_template(template_name)

    return HttpResponseNotFound(t.render(page.context_dict()))


def server_error(request, template_name="500.html"):
    """View handler for HTTP 500 Server Error responses."""
    if session.active_agency(request):
        session.update(request, origin=session.agency(request).index_url)
    else:
        session.update(request, origin=_index_url())

    home = viewmodels.Button.home(request)
    page = viewmodels.ErrorPage.error(button=home)
    t = loader.get_template(template_name)

    return HttpResponseServerError(t.render(page.context_dict()))
