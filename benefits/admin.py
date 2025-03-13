from django.conf import settings
from django.contrib.admin import AdminSite

from django.forms import ValidationError
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.models import Group
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator, decorator_from_middleware

from benefits.core.middleware import RecaptchaEnabled
from benefits.core.models import TransitAgency
from benefits.core import recaptcha, session


class BenefitsAdminLoginForm(AdminAuthenticationForm):

    def clean(self):
        if not recaptcha.verify(self.data):
            raise ValidationError("reCAPTCHA failed, please try again.")
        return super().clean()


class BenefitsAdminSite(AdminSite):

    site_title = "Cal-ITP Benefits Administrator"
    site_header = "Administrator"
    index_title = "Dashboard"
    login_form = BenefitsAdminLoginForm
    enable_nav_sidebar = False

    @method_decorator(decorator_from_middleware(RecaptchaEnabled))
    def login(self, request, extra_context=None):
        return super().login(request, extra_context)

    def __init__(self, name="admin"):
        super().__init__(name)
        self.enable_nav_sidebar = False

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
                transit_processor_portal_url = agency.transit_processor.portal_url

                context.update(
                    {
                        "has_permission_for_in_person": has_permission_for_in_person,
                        "transit_processor_portal_url": transit_processor_portal_url,
                        "title": f"{agency.long_name} | {self.index_title} | {self.site_title}",
                    }
                )

            return TemplateResponse(request, "admin/agency-dashboard-index.html", context)
