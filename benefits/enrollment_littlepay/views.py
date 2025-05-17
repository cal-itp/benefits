from django.template.response import TemplateResponse
from django.utils.decorators import decorator_from_middleware

from benefits.routes import routes
from benefits.core import session
from benefits.core.middleware import EligibleSessionRequired

from benefits.core import models
from benefits.enrollment import forms
from benefits.enrollment_littlepay.enrollment import enroll


@decorator_from_middleware(EligibleSessionRequired)
def index(request, enrollment_result_handler):
    # POST back after transit processor form, process card token
    if request.method == "POST":
        form = forms.CardTokenizeSuccessForm(request.POST)
        if not form.is_valid():
            raise Exception("Invalid card token form")

        card_token = form.cleaned_data.get("card_token")
        status, exception = enroll(request, card_token)

        return enrollment_result_handler(request, status, exception)

    # GET enrollment index
    else:
        agency = session.agency(request)
        flow = session.flow(request)

        tokenize_retry_form = forms.CardTokenizeFailForm(routes.ENROLLMENT_RETRY, "form-card-tokenize-fail-retry")
        tokenize_server_error_form = forms.CardTokenizeFailForm(routes.SERVER_ERROR, "form-card-tokenize-fail-server-error")
        tokenize_system_error_form = forms.CardTokenizeFailForm(
            routes.ENROLLMENT_SYSTEM_ERROR, "form-card-tokenize-fail-system-error"
        )
        tokenize_success_form = forms.CardTokenizeSuccessForm(
            action_url=routes.ENROLLMENT_INDEX, auto_id=True, label_suffix=""
        )

        # mapping from Django's I18N LANGUAGE_CODE to Littlepay's overlay language code
        overlay_language = {"en": "en", "es": "es-419"}.get(request.LANGUAGE_CODE, "en")

        context = {
            "forms": [tokenize_retry_form, tokenize_server_error_form, tokenize_system_error_form, tokenize_success_form],
            "cta_button": "tokenize_card",
            "enrollment_method": models.EnrollmentMethods.DIGITAL,
            "token_field": "card_token",
            "form_retry": tokenize_retry_form.id,
            "form_server_error": tokenize_server_error_form.id,
            "form_success": tokenize_success_form.id,
            "form_system_error": tokenize_system_error_form.id,
            "overlay_language": overlay_language,
        }
        context.update(flow.enrollment_index_context)

        return TemplateResponse(request, agency.enrollment_index_template, context)
