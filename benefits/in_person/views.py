import logging

from django.contrib.admin import site as admin_site
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import FormView

from benefits.core.models.transit import TransitAgency
from benefits.core import models, session
from benefits.eligibility import analytics as eligibility_analytics
from benefits.enrollment import analytics as enrollment_analytics
from benefits.enrollment.views import IndexView
from benefits.enrollment_littlepay.session import Session as LittlepaySession
from benefits.enrollment_littlepay.views import TokenView, IndexView as LittlepayIndexView
from benefits.enrollment_switchio.session import Session as SwitchioSession
from benefits.enrollment_switchio.views import GatewayUrlView, IndexView as SwitchioIndexView

from benefits.in_person import forms, mixins
from benefits.routes import routes

logger = logging.getLogger(__name__)


class EligibilityView(mixins.CommonContextMixin, FormView):
    """CBV for the in-person eligibility flow selection form."""

    template_name = "in_person/eligibility.html"
    form_class = forms.InPersonEligibilityForm

    def dispatch(self, request, *args, **kwargs):
        """Initialize session state before handling the request."""

        LittlepaySession(request, reset=True)
        SwitchioSession(request, reset=True)

        agency = session.agency(request)
        if not agency:
            agency = TransitAgency.for_user(request.user)
            session.update(request, agency=agency)
        self.agency = agency
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""

        kwargs = super().get_form_kwargs()
        kwargs["agency"] = self.agency
        return kwargs

    def form_valid(self, form):
        """If the form is valid, set enrollment flow, eligible session, and redirect."""

        flow_id = form.cleaned_data.get("flow")
        flow = models.EnrollmentFlow.objects.get(id=flow_id)
        session.update(self.request, flow=flow, eligible=True)
        eligibility_analytics.selected_flow(self.request, flow, enrollment_method=models.EnrollmentMethods.IN_PERSON)
        eligibility_analytics.started_eligibility(self.request, flow, enrollment_method=models.EnrollmentMethods.IN_PERSON)
        eligibility_analytics.returned_success(self.request, flow, enrollment_method=models.EnrollmentMethods.IN_PERSON)
        return redirect(routes.IN_PERSON_ENROLLMENT)


class LittlepayTokenView(TokenView):
    """View handler for the enrollment auth token."""

    enrollment_method = models.EnrollmentMethods.IN_PERSON
    route_system_error = routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR
    route_server_error = routes.IN_PERSON_SERVER_ERROR


class EnrollmentView(IndexView):

    route_origin = routes.IN_PERSON_ENROLLMENT

    def get_redirect_url(self, *args, **kwargs):
        route_name = self.agency.in_person_enrollment_index_route
        return reverse(route_name)


class LittlepayEnrollmentView(mixins.CommonContextMixin, LittlepayIndexView):
    """View handler for the in-person enrollment page."""

    enrollment_method = models.EnrollmentMethods.IN_PERSON
    route_enrollment_success = routes.IN_PERSON_ENROLLMENT_SUCCESS
    route_enrollment_retry = routes.IN_PERSON_ENROLLMENT_RETRY
    route_reenrollment_error = routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR
    route_server_error = routes.IN_PERSON_SERVER_ERROR
    route_system_error = routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR
    route_tokenize_success = routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX
    template_name = "in_person/enrollment/index_littlepay.html"

    def _get_verified_by(self):
        return f"{self.request.user.first_name} {self.request.user.last_name}"


def reenrollment_error(request):
    """View handler for a re-enrollment attempt that is not yet within the re-enrollment window."""

    agency = session.agency(request)
    context = {
        **admin_site.each_context(request),
        "title": f"{agency.long_name} | In-person enrollment | {admin_site.site_title}",
    }

    flow = session.flow(request)
    context["flow_label"] = flow.label

    return TemplateResponse(request, "in_person/enrollment/reenrollment_error.html", context)


def retry(request):
    """View handler for card verification failure."""
    # enforce POST-only route for sending analytics
    if request.method == "POST":
        enrollment_analytics.returned_retry(request, enrollment_method=models.EnrollmentMethods.IN_PERSON)

    agency = session.agency(request)
    context = {
        **admin_site.each_context(request),
        "title": f"{agency.long_name} | In-person enrollment | {admin_site.site_title}",
    }

    return TemplateResponse(request, "in_person/enrollment/retry.html", context)


def system_error(request):
    """View handler for an enrollment system error."""
    agency = session.agency(request)
    context = {
        **admin_site.each_context(request),
        "title": f"{agency.long_name} | In-person enrollment | {admin_site.site_title}",
    }

    return TemplateResponse(request, "in_person/enrollment/system_error.html", context)


def server_error(request):
    """View handler for errors caused by a misconfiguration or bad request."""
    agency = session.agency(request)
    context = {
        **admin_site.each_context(request),
        "title": f"{agency.long_name} | In-person enrollment | {admin_site.site_title}",
    }

    return TemplateResponse(request, "in_person/enrollment/server_error.html", context)


def success(request):
    """View handler for the final success page."""
    agency = session.agency(request)
    context = {
        **admin_site.each_context(request),
        "title": f"{agency.long_name} | In-person enrollment | {admin_site.site_title}",
    }

    return TemplateResponse(request, "in_person/enrollment/success.html", context)


class SwitchioGatewayUrlView(GatewayUrlView):
    enrollment_method = models.EnrollmentMethods.IN_PERSON
    route_redirect = routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX
    route_server_error = routes.IN_PERSON_SERVER_ERROR
    route_system_error = routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR


class SwitchioEnrollmentIndexView(mixins.CommonContextMixin, SwitchioIndexView):
    enrollment_method = models.EnrollmentMethods.IN_PERSON
    form_class = forms.CardTokenizeSuccessForm
    route_enrollment_success = routes.IN_PERSON_ENROLLMENT_SUCCESS
    route_reenrollment_error = routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR
    route_retry = routes.IN_PERSON_ENROLLMENT_RETRY
    route_server_error = routes.IN_PERSON_SERVER_ERROR
    route_system_error = routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR
    route_tokenize_success = routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX
    template_name = "in_person/enrollment/index_switchio.html"

    def _get_verified_by(self):
        return f"{self.request.user.first_name} {self.request.user.last_name}"

    def get_context_data(self, **kwargs):
        """Add in-person specific context data."""
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("state") == "tokenize":
            message = "Registering this contactless card for reduced fares..."
        else:
            message = "Connecting with payment processor..."

        context.update({"loading_message": message})
        return context

    def get(self, request, *args, **kwargs):
        if request.GET.get("error") == "canceled":
            # the user clicked the "Back" button on the Switchio tokenization gateway
            # send them back to the Admin index, similar to the Littlepay cancel button
            return redirect(routes.ADMIN_INDEX)

        return super().get(request, *args, **kwargs)
