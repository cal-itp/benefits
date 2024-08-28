from django.contrib.admin import site as admin_site
from django.template.response import TemplateResponse


def eligibility(request):
    return TemplateResponse(request, "in_person/eligibility.html")


def enrollment(request):
    context = {**admin_site.each_context(request)}

    return TemplateResponse(request, "in_person/enrollment.html", context)
