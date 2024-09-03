from django.contrib.admin import site as admin_site
from django.template.response import TemplateResponse

from benefits.core import session
from benefits.enrollment import forms
from benefits.enrollment.views import enrollment_get_context, enrollment_post
from benefits.routes import routes


def eligibility(request):
    # temporary change for testing only
    flow = session.agency(request).enrollment_flows.first()
    session.update(request, eligible=True, flow=flow)

    return TemplateResponse(request, "in_person/eligibility.html")


def enrollment(request):
    agency = session.agency(request)
    flow = session.flow(request)

    # POST back after transit processor form, process card token
    if request.method == "POST":
        return enrollment_post(request, agency, flow, success, reenrollment_error, system_error)
    # GET enrollment page
    else:
        tokenize_retry_form = forms.CardTokenizeFailForm(routes.IN_PERSON_ENROLLMENT_RETRY, "form-card-tokenize-fail-retry")
        tokenize_server_error_form = forms.CardTokenizeFailForm(routes.SERVER_ERROR, "form-card-tokenize-fail-server-error")
        tokenize_system_error_form = forms.CardTokenizeFailForm(
            routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR, "form-card-tokenize-fail-system-error"
        )
        tokenize_success_form = forms.CardTokenizeSuccessForm(
            data=None, action_url=routes.IN_PERSON_ENROLLMENT, auto_id=True, label_suffix=""
        )

        context = enrollment_get_context(
            request,
            agency,
            tokenize_retry_form=tokenize_retry_form,
            tokenize_server_error_form=tokenize_server_error_form,
            tokenize_system_error_form=tokenize_system_error_form,
            tokenize_success_form=tokenize_success_form,
        )
        context.update(**admin_site.each_context(request))

        return TemplateResponse(request, "in_person/enrollment.html", context)


def reenrollment_error(request):
    return TemplateResponse(request, "in_person/enrollment/reenrollment_error.html")


def retry(request):
    return TemplateResponse(request, "in_person/enrollment/retry.html")


def success(request):
    return TemplateResponse(request, "in_person/enrollment/success.html")


def system_error(request):
    return TemplateResponse(request, "in_person/enrollment/system_error.html")
