from django.contrib.admin import site as admin_site
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.urls import reverse


from benefits.routes import routes
from benefits.core import session
from benefits.core.models import EnrollmentFlow

from benefits.in_person import forms


def eligibility(request):
    """View handler for the in-person eligibility flow selection form."""

    agency = session.agency(request)
    context = {**admin_site.each_context(request), "form": forms.InPersonEligibilityForm(agency=agency)}

    if request.method == "POST":
        form = forms.InPersonEligibilityForm(data=request.POST, agency=agency)

        if form.is_valid():
            flow_id = form.cleaned_data.get("flow")
            flow = EnrollmentFlow.objects.get(id=flow_id)
            session.update(request, flow=flow)

            in_person_enrollment = reverse(routes.IN_PERSON_ENROLLMENT)
            response = redirect(in_person_enrollment)
        else:
            context["form"] = form
            response = TemplateResponse(request, "in_person/eligibility.html", context)
    else:
        response = TemplateResponse(request, "in_person/eligibility.html", context)

    return response


def enrollment(request):
    if request.method == "POST":
        pass
    # GET enrollment index
    else:
        agency = session.agency(request)

        tokenize_retry_form = forms.CardTokenizeFailForm(routes.ENROLLMENT_RETRY, "form-card-tokenize-fail-retry")
        tokenize_server_error_form = forms.CardTokenizeFailForm(routes.SERVER_ERROR, "form-card-tokenize-fail-server-error")
        tokenize_system_error_form = forms.CardTokenizeFailForm(
            routes.ENROLLMENT_SYSTEM_ERROR, "form-card-tokenize-fail-system-error"
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
        }

        return TemplateResponse(request, "in_person/enrollment.html", context)
