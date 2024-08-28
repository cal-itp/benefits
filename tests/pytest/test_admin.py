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
def test_admin_override_agency_user_customer_service(app_request, model_AgencyUser, model_TransitAgency):
    app_request.user = model_AgencyUser

    # set up TransitAgency with staff_group and customer_service_group
    model_TransitAgency.pk = None
    model_TransitAgency.staff_group = Group.objects.get(name="CST")
    customer_service_group = Group.objects.create(name="CST Customer Service")
    model_TransitAgency.customer_service_group = customer_service_group
    model_TransitAgency.save()

    # add the user to the customer service group
    model_AgencyUser.groups.add(customer_service_group)

    response = BenefitsAdminSite().index(app_request)

    assert response.status_code == 200
    assert response.template_name == "admin/agency-dashboard-index.html"
    assert response.context_data["has_permission_for_in_person"] is True


@pytest.mark.django_db
def test_admin_override_agency_user_not_customer_service(app_request, model_AgencyUser, model_TransitAgency):
    app_request.user = model_AgencyUser

    # set up TransitAgency with only a staff_group
    model_TransitAgency.pk = None
    model_TransitAgency.staff_group = Group.objects.get(name="CST")
    model_TransitAgency.save()

    response = BenefitsAdminSite().index(app_request)

    assert response.status_code == 200
    assert response.template_name == "admin/agency-dashboard-index.html"
    assert response.context_data["has_permission_for_in_person"] is False


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
