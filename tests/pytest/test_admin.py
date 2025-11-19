import pytest
from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import reverse
from benefits.admin import BenefitsAdminLoginForm
from benefits.core.mixins import ValidateRecaptchaMixin
from benefits.routes import routes


class TestBenefitsAdminLoginForm:
    @pytest.fixture(autouse=True)
    def init(self):
        self.form = BenefitsAdminLoginForm()

    def test_recaptcha_mixin(self):
        assert isinstance(self.form, ValidateRecaptchaMixin)


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
def test_admin_override_agency_user_customer_service(model_AgencyUser, model_TransitAgency, client):
    url = reverse(routes.ADMIN_INDEX)
    client.force_login(model_AgencyUser)

    # set up TransitAgency with staff_group and customer_service_group
    model_TransitAgency.pk = None
    model_TransitAgency.staff_group = Group.objects.get(name="CST")
    customer_service_group = Group.objects.create(name="CST Customer Service")
    model_TransitAgency.customer_service_group = customer_service_group
    model_TransitAgency.save()

    # add the user to the customer service group
    model_AgencyUser.groups.add(customer_service_group)

    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == "admin/agency-dashboard-index.html"
    assert response.context_data["has_permission_for_in_person"] is True


@pytest.mark.django_db
def test_admin_override_agency_user_not_customer_service(model_AgencyUser, model_TransitAgency, client):
    url = reverse(routes.ADMIN_INDEX)
    client.force_login(model_AgencyUser)

    # set up TransitAgency with only a staff_group
    model_TransitAgency.pk = None
    model_TransitAgency.staff_group = Group.objects.get(name="CST")
    model_TransitAgency.save()

    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == "admin/agency-dashboard-index.html"
    assert response.context_data["has_permission_for_in_person"] is False


@pytest.mark.django_db
def test_admin_override_staff_group_user(model_StaffGroupUser, client):
    url = reverse(routes.ADMIN_INDEX)
    client.force_login(model_StaffGroupUser)
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == "admin/index.html"


@pytest.mark.django_db
def test_admin_override_super_user(model_SuperUser, client):
    url = reverse(routes.ADMIN_INDEX)
    client.force_login(model_SuperUser)
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == "admin/index.html"
