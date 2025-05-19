from django.template.response import TemplateResponse
from django.views.generic import FormView

from benefits.routes import routes
from benefits.core import session

from benefits.core import models
from benefits.enrollment import forms
from benefits.enrollment_littlepay.enrollment import enroll


class IndexView(FormView):
    template_name = "enrollment_littlepay/index.html"
    enrollment_result_handler = None

    def get(self, request, *args, **kwargs):
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

        enrollment_index_context_dict = flow.enrollment_index_context

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

        enrollment_index_context_dict["transit_processor"] = transit_processor_context
        context.update(enrollment_index_context_dict)

        return TemplateResponse(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # POST back after transit processor form, process card token
        form = forms.CardTokenizeSuccessForm(request.POST)
        if not form.is_valid():
            raise Exception("Invalid card token form")

        card_token = form.cleaned_data.get("card_token")
        status, exception = enroll(request, card_token)

        return self.enrollment_result_handler(request, status, exception)
