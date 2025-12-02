"""
The enrollment application: view definitions for the benefits enrollment flow.
"""

from dataclasses import asdict, dataclass
import logging

from django.template.defaultfilters import date
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

from benefits.core.context.agency import AgencySlug
from benefits.core.context.flow import SystemName
from benefits.core.context import formatted_gettext_lazy as _
from benefits.routes import routes
from benefits.core import models, session
from benefits.core.mixins import (
    AgencySessionRequiredMixin,
    EligibleSessionRequiredMixin,
    FlowSessionRequiredMixin,
    PageViewMixin,
)
from . import analytics

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
            does_not_expire_until = _("Your CalFresh Cardholder transit benefit does not expire until")
            reenroll_on = _("You can re-enroll for this benefit beginning on")
            try_again = _("Please try again then.")

            context["paragraphs"] = [
                f"{does_not_expire_until} {date(expiry)}. {reenroll_on} {date(reenrollment)}. {try_again}"
            ]

        return context

    def get(self, request, *args, **kwargs):
        flow = self.flow

        if session.logged_in(request) and flow.supports_sign_out:
            # overwrite origin for a logged in user
            # if they click the logout button, they are taken to the new route
            session.update(request, origin=reverse(routes.LOGGED_OUT))

        return super().get(request, *args, **kwargs)


class RetryView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, EligibleSessionRequiredMixin, TemplateView):
    """View handler for a recoverable failure condition."""

    template_name = "enrollment/retry.html"
    enrollment_method = models.EnrollmentMethods.DIGITAL

    def dispatch(self, request, *args, **kwargs):
        # for Littlepay, the Javascript in enrollment_littlepay/index.html sends a form POST to this view
        # to simplify, we check the method here and process POSTs rather than implementing as a FormView, which requires
        # instantiating the enrollment.forms.CardTokenizeFailForm, needing additional parameters such as a form id and
        # action_url, that are already specified in the enrollment_littlepay/views.IndexView
        #
        # Switchio doesn't use this view at all

        # call super().dispatch() first to ensure all mixins are processed (i.e. so we have a self.flow and self.agency)
        response = super().dispatch(request, *args, **kwargs)
        if request.method == "POST":
            enrollment_group = self.flow.group_id
            transit_processor = self.agency.transit_processor
            analytics.returned_retry(
                request,
                enrollment_group=enrollment_group,
                transit_processor=transit_processor,
                enrollment_method=self.enrollment_method,
            )
            # TemplateView doesn't implement POST, just return the template via GET
            return super().get(request, *args, **kwargs)
        # for other request methods, we don't want/need to serve the retry template since users should only arrive via the form
        # POST, returning super().dispatch() results in a 200 User Error response
        return response


class SystemErrorView(AgencySessionRequiredMixin, FlowSessionRequiredMixin, EligibleSessionRequiredMixin, TemplateView):
    """View handler for an enrollment system error."""

    template_name = TEMPLATE_SYSTEM_ERROR

    def get(self, request, *args, **kwargs):
        # overwrite origin so that CTA takes user to agency index
        agency = self.agency
        session.update(request, origin=agency.index_url)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


@dataclass
class EnrollmentSuccess:
    success_message: str
    thank_you_message: str

    def dict(self):
        return asdict(self)


class DefaultEnrollmentSuccess(EnrollmentSuccess):
    def __init__(self, transportation_type):
        super().__init__(
            success_message=_(
                "You were not charged anything today. When boarding {transportation_type}, tap your contactless card and you "
                "will be charged a reduced fare. You will need to re-enroll if you choose to change the card you use to "
                "pay for transit service.",
                transportation_type=transportation_type,
            ),
            thank_you_message=_("Thank you for using Cal-ITP Benefits!"),
        )


class AgencyCardEnrollmentSuccess(EnrollmentSuccess):
    def __init__(self, transit_benefit, transportation_type):
        super().__init__(
            success_message=_(
                "Your contactless card is now enrolled in {transit_benefit}. When boarding {transportation_type}, tap this "
                "card and you will be charged a reduced fare. You will need to re-enroll if you choose to change the card you "
                "use to pay for transit service.",
                transit_benefit=transit_benefit,
                transportation_type=transportation_type,
            ),
            thank_you_message=_("You were not charged anything today. Thank you for using Cal-ITP Benefits!"),
        )


class SuccessView(PageViewMixin, FlowSessionRequiredMixin, EligibleSessionRequiredMixin, TemplateView):
    """View handler for the final success page."""

    template_name = "enrollment/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.request
        flow = self.flow

        context = {"redirect_to": request.path}
        copy = {
            AgencySlug.CST.value: DefaultEnrollmentSuccess(transportation_type=_("a CST bus")),
            AgencySlug.EDCTA.value: DefaultEnrollmentSuccess(transportation_type=_("an EDCTA bus")),
            AgencySlug.MST.value: DefaultEnrollmentSuccess(transportation_type=_("an MST bus")),
            AgencySlug.NEVCO.value: DefaultEnrollmentSuccess(transportation_type=_("a Nevada County Connects bus")),
            AgencySlug.RABA.value: DefaultEnrollmentSuccess(transportation_type=_("a RABA bus")),
            AgencySlug.SACRT.value: DefaultEnrollmentSuccess(transportation_type=_("a SacRT bus")),
            AgencySlug.SLORTA.value: DefaultEnrollmentSuccess(transportation_type=_("a RTA bus")),
            AgencySlug.SBMTD.value: DefaultEnrollmentSuccess(transportation_type=_("an SBMTD bus")),
            AgencySlug.VCTC.value: DefaultEnrollmentSuccess(
                transportation_type=_("a Ventura County Transportation Commission bus")
            ),
            SystemName.AGENCY_CARD.value: AgencyCardEnrollmentSuccess(
                transit_benefit=_("a CST Agency Card transit benefit"), transportation_type=_("a CST bus")
            ),
            SystemName.COURTESY_CARD.value: AgencyCardEnrollmentSuccess(
                transit_benefit=_("an MST Courtesy Card transit benefit"), transportation_type="an MST bus"
            ),
            SystemName.REDUCED_FARE_MOBILITY_ID.value: AgencyCardEnrollmentSuccess(
                transit_benefit=_("an SBMTD Reduced Fare Mobility ID transit benefit"), transportation_type=_("an SBMTD bus")
            ),
        }

        if flow.uses_api_verification:
            copy_context = copy[flow.system_name].dict()
        else:
            copy_context = copy[flow.transit_agency.slug].dict()

        context.update(copy_context)

        return context

    def get(self, request, *args, **kwargs):
        session.update(request, origin=reverse(routes.ENROLLMENT_SUCCESS))

        flow = self.flow

        if session.logged_in(request) and flow.supports_sign_out:
            # overwrite origin for a logged in user
            # if they click the logout button, they are taken to the new route
            session.update(request, origin=reverse(routes.LOGGED_OUT))

        return super().get(request, *args, **kwargs)
