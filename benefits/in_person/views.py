from django.template.response import TemplateResponse

ROUTE_ELIGIBILITY = "in_person:eligibility"
ROUTE_ENROLLMENT = "in_person:enrollment"


def eligibility(request):
    return TemplateResponse(request, "in_person/eligibility.html")


def enrollment(request):
    return TemplateResponse(request, "in_person/enrollment.html")
