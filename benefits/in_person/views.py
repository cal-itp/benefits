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
    context = {**admin_site.each_context(request)}

    return TemplateResponse(request, "in_person/enrollment.html", context)
