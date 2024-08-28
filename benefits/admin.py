from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.response import TemplateResponse
from benefits.core.models import TransitAgency
from benefits.core import session


class BenefitsAdminSite(admin.AdminSite):

    def index(self, request, extra_context=None):
        """
        Display the main admin index page if the user is a superuser or a "staff_group" user.
        Display the agency dashboard index page if the user is an agency user.
        get_app_list returns a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = self.get_app_list(request)

        context = {
            **self.each_context(request),
            "title": self.index_title,
            "subtitle": None,
            "app_list": app_list,
            **(extra_context or {}),
        }

        request.current_app = self.name

        staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
        if request.user.is_superuser or request.user.groups.filter(name=staff_group).exists():
            return TemplateResponse(request, "admin/index.html", context)
        else:
            agency = TransitAgency.for_user(request.user)
            session.update(request, agency=agency)

            if agency is not None:
                has_permission_for_in_person = agency.customer_service_group in request.user.groups.all()
                context.update({"has_permission_for_in_person": has_permission_for_in_person})

            return TemplateResponse(request, "admin/agency-dashboard-index.html", context)
