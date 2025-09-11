"""
The enrollment application: view definitions for the benefits enrollment flow.
"""

import logging

from django.template.defaultfilters import date
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware
from django.views.generic import RedirectView, TemplateView

from benefits.core.context.flow import SystemName
from benefits.core.context import formatted_gettext_lazy as _
from benefits.routes import routes
from benefits.core import session
from benefits.core.mixins import AgencySessionRequiredMixin, EligibleSessionRequiredMixin, FlowSessionRequiredMixin
from benefits.core.middleware import EligibleSessionRequired, FlowSessionRequired, pageview_decorator

from . import analytics

TEMPLATE_RETRY = "enrollment/retry.html"
TEMPLATE_SYSTEM_ERROR = "enrollment/system_error.html"


logger = logging.getLogger(__name__)


class IndexView(AgencySessionRequiredMixin, EligibleSessionRequiredMixin, RedirectView):
    """CBV for the enrollment landing page."""

    route_origin = routes.ENROLLMENT_INDEX

    def get_redirect_url(self, *args, **kwargs):
        route_name = self.agency.enrollment_index_route
        return reverse(route_name)

    def get(self, request, *args, **kwargs):
        session.update(request, origin=reverse(self.route_origin))
        return super().get(request, *args, **kwargs)


class ReenrollmentErrorView(FlowSessionRequiredMixin, EligibleSessionRequiredMixin, TemplateView):
    """View handler for a re-enrollment attempt that is not yet within the re-enrollment window."""

    template_name = "enrollment/reenrollment-error.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.request

        flow = self.flow
        expiry = session.enrollment_expiry(request)
        reenrollment = session.enrollment_reenrollment(request)

        if flow.system_name == SystemName.CALFRESH:
            context["paragraphs"] = [
                f"{_("Your CalFresh Cardholder transit benefit does not expire until")} {date(expiry)}. "
                + f"{_("You can re-enroll for this benefit beginning on")} {date(reenrollment)}. {_("Please try again then.")}"
            ]
        else:
            raise Exception(f"Re-enrollment error not supported for flow {flow.system_name}")

        return context

    def get(self, request, *args, **kwargs):
        flow = self.flow

        if session.logged_in(request) and flow.supports_sign_out:
            # overwrite origin for a logged in user
            # if they click the logout button, they are taken to the new route
            session.update(request, origin=reverse(routes.LOGGED_OUT))

        return super().get(request, *args, **kwargs)


@decorator_from_middleware(EligibleSessionRequired)
def retry(request):
    """View handler for a recoverable failure condition."""
    analytics.returned_retry(request)
    return TemplateResponse(request, TEMPLATE_RETRY)


@decorator_from_middleware(EligibleSessionRequired)
def system_error(request):
    """View handler for an enrollment system error."""

    # overwrite origin so that CTA takes user to agency index
    agency = session.agency(request)
    session.update(request, origin=agency.index_url)

    return TemplateResponse(request, TEMPLATE_SYSTEM_ERROR)


@pageview_decorator
@decorator_from_middleware(EligibleSessionRequired)
@decorator_from_middleware(FlowSessionRequired)
def success(request):
    """View handler for the final success page."""
    request.path = "/enrollment/success"
    session.update(request, origin=reverse(routes.ENROLLMENT_SUCCESS))

    flow = session.flow(request)

    if session.logged_in(request) and flow.supports_sign_out:
        # overwrite origin for a logged in user
        # if they click the logout button, they are taken to the new route
        session.update(request, origin=reverse(routes.LOGGED_OUT))

    context = {"redirect_to": request.path}
    context.update(flow.enrollment_success_context)

    return TemplateResponse(request, "enrollment/success.html", context)
