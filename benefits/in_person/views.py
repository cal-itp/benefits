from django.template.response import TemplateResponse


def eligibility(request):
    return TemplateResponse(request, "in_person/eligibility.html")


def enrollment(request):
    return TemplateResponse(request, "in_person/enrollment.html")
