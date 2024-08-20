import pytest
from django.conf import settings
from django.contrib.auth.models import Group, User
from benefits.admin import BenefitsAdminSite


@pytest.fixture
def model_User():
    return User.objects.create(is_active="1", is_staff="1")


@pytest.fixture
def model_AgencyUser(model_User):
    cst_group = Group.objects.create(name="CST")
    model_User.groups.add(cst_group)
    model_User.save()
    return model_User


@pytest.fixture
def model_SuperAgencyUser(model_User):
    model_User.groups.add(Group.objects.get(name=settings.STAFF_GROUP_NAME))
    model_User.save()
    return model_User


@pytest.fixture
def model_SuperUser(model_User):
    model_User.is_superuser = "1"
    model_User.save()
    return model_User


@pytest.mark.django_db
def test_admin_override_agency_user(app_request, model_AgencyUser):
    app_request.user = model_AgencyUser
    response = BenefitsAdminSite().index(app_request)

    assert response.status_code == 200
    assert response.template_name == "admin/agency-dashboard-index.html"


@pytest.mark.django_db
def test_admin_override_super_agency_user(app_request, model_SuperAgencyUser):
    app_request.user = model_SuperAgencyUser
    response = BenefitsAdminSite().index(app_request)

    assert response.status_code == 200
    assert response.template_name == "admin/index.html"


@pytest.mark.django_db
def test_admin_override_super_user(app_request, model_SuperUser):
    app_request.user = model_SuperUser
    response = BenefitsAdminSite().index(app_request)

    assert response.status_code == 200
    assert response.template_name == "admin/index.html"
