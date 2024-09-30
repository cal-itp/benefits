import logging

from django.contrib.admin import site as admin_site
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.urls import reverse
import sentry_sdk


from benefits.routes import routes
from benefits.core import models, session
from benefits.enrollment.enrollment import Status, request_card_tokenization_access, enroll

from benefits.in_person import forms

logger = logging.getLogger(__name__)


def eligibility(request):
    """View handler for the in-person eligibility flow selection form."""

    agency = session.agency(request)
    context = {
        **admin_site.each_context(request),
        "form": forms.InPersonEligibilityForm(agency=agency),
        "title": f"{agency.long_name} | In-person enrollment | {admin_site.site_title}",
    }

    if request.method == "POST":
        form = forms.InPersonEligibilityForm(data=request.POST, agency=agency)

        if form.is_valid():
            flow_id = form.cleaned_data.get("flow")
            flow = models.EnrollmentFlow.objects.get(id=flow_id)
            session.update(request, flow=flow)

            in_person_enrollment = reverse(routes.IN_PERSON_ENROLLMENT)
            response = redirect(in_person_enrollment)
        else:
            context["form"] = form
            response = TemplateResponse(request, "in_person/eligibility.html", context)
    else:
        response = TemplateResponse(request, "in_person/eligibility.html", context)

    return response


def token(request):
    """View handler for the enrollment auth token."""
    if not session.enrollment_token_valid(request):
        response = request_card_tokenization_access(request)

        if response.status is Status.SUCCESS:
            session.update(request, enrollment_token=response.access_token, enrollment_token_exp=response.expires_at)
        elif response.status is Status.SYSTEM_ERROR or response.status is Status.EXCEPTION:
            logger.debug("Error occurred while requesting access token", exc_info=response.exception)
            sentry_sdk.capture_exception(response.exception)

            if response.status is Status.SYSTEM_ERROR:
                redirect = reverse(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)
            else:
                redirect = reverse(routes.IN_PERSON_SERVER_ERROR)

            data = {"redirect": redirect}
            return JsonResponse(data)

    data = {"token": session.enrollment_token(request)}

    return JsonResponse(data)


def enrollment(request):
    """View handler for the in-person enrollment page."""
    # POST back after transit processor form, process card token
    if request.method == "POST":
        form = forms.CardTokenizeSuccessForm(request.POST)
        if not form.is_valid():
            raise Exception("Invalid card token form")

        card_token = form.cleaned_data.get("card_token")
        status, exception = enroll(request, card_token)

        match (status):
            case Status.SUCCESS:
                agency = session.agency(request)
                flow = session.flow(request)
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
                return redirect(routes.IN_PERSON_ENROLLMENT_SUCCESS)

            case Status.SYSTEM_ERROR:
                sentry_sdk.capture_exception(exception)
                return redirect(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)

            case Status.EXCEPTION:
                sentry_sdk.capture_exception(exception)
                return redirect(routes.IN_PERSON_SERVER_ERROR)

            case Status.REENROLLMENT_ERROR:
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
            "card_tokenize_env": agency.transit_processor.card_tokenize_env,
            "card_tokenize_func": agency.transit_processor.card_tokenize_func,
            "card_tokenize_url": agency.transit_processor.card_tokenize_url,
            "token_field": "card_token",
            "form_retry": tokenize_retry_form.id,
            "form_server_error": tokenize_server_error_form.id,
            "form_success": tokenize_success_form.id,
            "form_system_error": tokenize_system_error_form.id,
            "title": f"{agency.long_name} | In-person enrollment | {admin_site.site_title}",
        }

        return TemplateResponse(request, "in_person/enrollment.html", context)


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
