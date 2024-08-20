from django.contrib.admin.apps import AdminConfig


class BenefitsAdminConfig(AdminConfig):
    default_site = "benefits.admin.BenefitsAdminSite"
