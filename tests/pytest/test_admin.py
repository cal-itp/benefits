import pytest
from django.conf import settings
from django.contrib.auth.models import Group, User
from benefits.admin import BenefitsAdminSite


@pytest.fixture
def model_User():
    return User.objects.create(is_active=True, is_staff=True)


@pytest.fixture
def model_AgencyUser(model_User):
    cst_group = Group.objects.create(name="CST")
    model_User.groups.add(cst_group)
    model_User.save()
    return model_User


@pytest.fixture
def model_StaffGroupUser(model_User):
    model_User.groups.add(Group.objects.get(name=settings.STAFF_GROUP_NAME))
    model_User.save()
    return model_User


@pytest.fixture
def model_SuperUser(model_User):
    model_User.is_superuser = True
    model_User.save()
    return model_User


@pytest.mark.django_db
def test_admin_override_agency_user(app_request, model_AgencyUser):
    app_request.user = model_AgencyUser
    response = BenefitsAdminSite().index(app_request)

    assert response.status_code == 200
    assert response.template_name == "admin/agency-dashboard-index.html"


@pytest.mark.django_db
def test_admin_override_staff_group_user(app_request, model_StaffGroupUser):
    app_request.user = model_StaffGroupUser
    response = BenefitsAdminSite().index(app_request)

    assert response.status_code == 200
    assert response.template_name == "admin/index.html"


@pytest.mark.django_db
def test_admin_override_super_user(app_request, model_SuperUser):
    app_request.user = model_SuperUser
    response = BenefitsAdminSite().index(app_request)

    assert response.status_code == 200
    assert response.template_name == "admin/index.html"
