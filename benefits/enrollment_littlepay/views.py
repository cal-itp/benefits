from django.template.response import TemplateResponse
from django.utils.decorators import decorator_from_middleware
import sentry_sdk

from benefits.routes import routes
from benefits.core import session
from benefits.core.middleware import EligibleSessionRequired

from benefits.core import models
from benefits.enrollment import analytics, forms
from benefits.enrollment.enrollment import Status
from benefits.enrollment.views import success, system_error, reenrollment_error
from benefits.enrollment_littlepay.enrollment import enroll


@decorator_from_middleware(EligibleSessionRequired)
def index(request):
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
                oauth_extra_claims = session.oauth_extra_claims(request)
                # EnrollmentEvent expects a string value for extra_claims
                if oauth_extra_claims:
                    str_extra_claims = ", ".join(oauth_extra_claims)
                else:
                    str_extra_claims = ""
                event = models.EnrollmentEvent.objects.create(
                    transit_agency=agency,
                    enrollment_flow=flow,
                    enrollment_method=models.EnrollmentMethods.DIGITAL,
                    verified_by=flow.eligibility_verifier,
                    expiration_datetime=expiry,
                    extra_claims=str_extra_claims,
                )
                event.save()
                analytics.returned_success(request, flow.group_id, extra_claims=oauth_extra_claims)
                return success(request)

            case Status.SYSTEM_ERROR:
                analytics.returned_error(request, str(exception))
                sentry_sdk.capture_exception(exception)
                return system_error(request)

            case Status.EXCEPTION:
                analytics.returned_error(request, str(exception))
                raise exception

            case Status.REENROLLMENT_ERROR:
                return reenrollment_error(request)

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
