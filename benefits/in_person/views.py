import logging

from django.contrib.admin import site as admin_site
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView
import sentry_sdk


from benefits.core.models.transit import TransitAgency
from benefits.routes import routes
from benefits.core import models, session
from benefits.eligibility import analytics as eligibility_analytics
from benefits.enrollment import analytics as enrollment_analytics
from benefits.enrollment.enrollment import Status
from benefits.enrollment_littlepay.enrollment import get_card_types_for_js, request_card_tokenization_access, enroll
from benefits.enrollment_littlepay.session import Session as LittlepaySession

from benefits.in_person import forms

logger = logging.getLogger(__name__)


class EligibilityView(FormView):
    """CBV for the in-person eligibility flow selection form."""

    template_name = "in_person/eligibility.html"
    form_class = forms.InPersonEligibilityForm

    def dispatch(self, request, *args, **kwargs):
        """Initialize session state before handling the request."""

        agency = session.agency(request)
        if not agency:
            agency = TransitAgency.for_user(request.user)
            session.update(request, agency=agency)
        self.agency = agency
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add in-person specific context data."""

        context = super().get_context_data(**kwargs)
        context.update(
            {
                **admin_site.each_context(self.request),
                "title": f"{self.agency.long_name} | In-person enrollment | {admin_site.site_title}",
            }
        )
        return context

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


def token(request):
    """View handler for the enrollment auth token."""
    session = LittlepaySession(request)

    if not session.access_token_valid():
        response = request_card_tokenization_access(request)

        if response.status is Status.SUCCESS:
            session.access_token = response.access_token
            session.access_token_expiry = response.expires_at
        elif response.status is Status.SYSTEM_ERROR or response.status is Status.EXCEPTION:
            logger.debug("Error occurred while requesting access token", exc_info=response.exception)
            sentry_sdk.capture_exception(response.exception)
            enrollment_analytics.failed_pretokenization_request(
                request, response.status_code, enrollment_method=models.EnrollmentMethods.IN_PERSON
            )

            if response.status is Status.SYSTEM_ERROR:
                redirect = reverse(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)
            else:
                redirect = reverse(routes.IN_PERSON_SERVER_ERROR)

            data = {"redirect": redirect}
            return JsonResponse(data)

    data = {"token": session.access_token}

    return JsonResponse(data)


def enrollment(request):
    """View handler for the in-person enrollment page."""
    # POST back after transit processor form, process card token
    if request.method == "POST":
        form = forms.CardTokenizeSuccessForm(request.POST)
        if not form.is_valid():
            raise Exception("Invalid card token form")

        flow = session.flow(request)
        card_token = form.cleaned_data.get("card_token")
        status, exception = enroll(request, card_token)

        match (status):
            case Status.SUCCESS:
                agency = session.agency(request)
                expiry = session.enrollment_expiry(request)
                verified_by = f"{request.user.first_name} {request.user.last_name}"
                event = models.EnrollmentEvent.objects.create(
                    transit_agency=agency,
                    enrollment_flow=flow,
                    enrollment_method=models.EnrollmentMethods.IN_PERSON,
                    verified_by=verified_by,
                    expiration_datetime=expiry,
                )
                event.save()
                enrollment_analytics.returned_success(
                    request, flow.group_id, enrollment_method=models.EnrollmentMethods.IN_PERSON
                )
                return redirect(routes.IN_PERSON_ENROLLMENT_SUCCESS)

            case Status.SYSTEM_ERROR:
                enrollment_analytics.returned_error(
                    request, str(exception), enrollment_method=models.EnrollmentMethods.IN_PERSON
                )
                sentry_sdk.capture_exception(exception)
                return redirect(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)

            case Status.EXCEPTION:
                enrollment_analytics.returned_error(
                    request, str(exception), enrollment_method=models.EnrollmentMethods.IN_PERSON
                )
                sentry_sdk.capture_exception(exception)
                return redirect(routes.IN_PERSON_SERVER_ERROR)

            case Status.REENROLLMENT_ERROR:
                enrollment_analytics.returned_error(
                    request, "Re-enrollment error.", enrollment_method=models.EnrollmentMethods.IN_PERSON
                )
                return redirect(routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR)
    # GET enrollment index
    else:
        agency = session.agency(request)

        tokenize_retry_form = forms.CardTokenizeFailForm(routes.IN_PERSON_ENROLLMENT_RETRY, "form-card-tokenize-fail-retry")
        tokenize_server_error_form = forms.CardTokenizeFailForm(
            routes.IN_PERSON_SERVER_ERROR, "form-card-tokenize-fail-server-error"
        )
        tokenize_system_error_form = forms.CardTokenizeFailForm(
            routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR, "form-card-tokenize-fail-system-error"
        )
        tokenize_success_form = forms.CardTokenizeSuccessForm(
            action_url=routes.IN_PERSON_ENROLLMENT, auto_id=True, label_suffix=""
        )

        context = {
            **admin_site.each_context(request),
            "forms": [tokenize_retry_form, tokenize_server_error_form, tokenize_system_error_form, tokenize_success_form],
            "cta_button": "tokenize_card",
            "enrollment_method": models.EnrollmentMethods.IN_PERSON,
            "token_field": "card_token",
            "form_retry": tokenize_retry_form.id,
            "form_server_error": tokenize_server_error_form.id,
            "form_success": tokenize_success_form.id,
            "form_system_error": tokenize_system_error_form.id,
            "title": f"{agency.long_name} | In-person enrollment | {admin_site.site_title}",
            "card_types": get_card_types_for_js(),
        }

        match agency.littlepay_config.environment:
            case models.Environment.QA.value:
                url = "https://verify.qa.littlepay.com/assets/js/littlepay.min.js"
                card_tokenize_env = "https://verify.qa.littlepay.com"
            case models.Environment.PROD.value:
                url = "https://verify.littlepay.com/assets/js/littlepay.min.js"
                card_tokenize_env = "https://verify.littlepay.com"
            case _:
                raise ValueError("Unrecognized environment value")

        transit_processor_context = dict(
            name="Littlepay", website="https://littlepay.com", card_tokenize_url=url, card_tokenize_env=card_tokenize_env
        )
        context.update({"transit_processor": transit_processor_context})

        return TemplateResponse(request, "in_person/enrollment/index.html", context)


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
