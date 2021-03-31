"""
The core application: view definition for the root of the webapp.
"""
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import pgettext, ugettext as _

from . import models, session, viewmodels


def PageTemplateResponse(request, page_vm):
    """Helper returns a TemplateResponse using the common page template."""
    return TemplateResponse(request, "core/page.html", page_vm.context_dict())


def _index_content_title():
    """Helper returns the content title for the common index page."""
    return _("core.index.content_title")


def _index_image():
    """Helper returns a viewmodels.Image for the common index page."""
    return viewmodels.Image("riderboardingbusandtapping.svg", pgettext("image alt text", "core.index.image"))


def _index_paragraphs():
    """Helper returns the content paragraphs for the common index page."""
    return [_("core.index.p1"), _("core.index.p2"), _("core.index.p3")]


def _index_url():
    """Helper computes the index url path."""
    return reverse("core:index")


def index(request):
    """View handler for the main entry page."""
    session.reset(request)

    # generate a button to the landing page for each active agency
    agencies = models.TransitAgency.all_active()
    buttons = [viewmodels.Button.outline_primary(text=a.short_name, url=a.index_url) for a in agencies]
    buttons[0].classes.append("mt-3")
    buttons[0].label = _("core.index.chooseprovider")

    page = viewmodels.Page(
        content_title=_index_content_title(),
        paragraphs=_index_paragraphs(),
        image=_index_image(),
        buttons=buttons,
        classes="home",
    )

    return PageTemplateResponse(request, page)


def agency_index(request, agency):
    """View handler for an agency entry page."""
    session.reset(request)
    session.update(request, agency=agency, origin=agency.index_url)

    page = viewmodels.Page(
        content_title=_index_content_title(),
        paragraphs=_index_paragraphs(),
        image=_index_image(),
        button=viewmodels.Button.primary(text=_("core.index.continue"), url=reverse("eligibility:index")),
        classes="home",
    )

    return PageTemplateResponse(request, page)


def help(request):
    """View handler for the help page."""
    if session.active_agency(request):
        agency = session.agency(request)
        buttons = [viewmodels.Button.agency_phone_link(agency)]
    else:
        buttons = [viewmodels.Button.agency_phone_link(a) for a in models.TransitAgency.all_active()]

    buttons.append(viewmodels.Button.home(request, _("core.buttons.back")))

    page = viewmodels.Page(
        title=_("core.help"),
        content_title=_("core.help"),
        paragraphs=[_("core.help.p1"), _("core.help.p2")],
        buttons=buttons,
        classes="text-lg-center",
    )

    return TemplateResponse(request, "core/help.html", page.context_dict())


def payment_options(request):
    """View handler for the Payment Options page."""
    page = viewmodels.Page(
        title=_("core.payment-options"),
        icon=viewmodels.Icon("bankcard", pgettext("image alt text", "core.icons.bankcard")),
        content_title=_("core.payment-options"),
        buttons=viewmodels.Button.home(request, text=_("core.buttons.back")),
    )

    return TemplateResponse(request, "core/payment-options.html", page.context_dict())


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
