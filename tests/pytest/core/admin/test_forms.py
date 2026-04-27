import pytest

from benefits.core.admin.forms import BenefitsPasswordResetForm, BenefitsSetPasswordForm, TransitAgencyGroupForm
from benefits.core.mixins import ValidateRecaptchaMixin
from benefits.core.models import Environment, TransitAgency
from benefits.enrollment_switchio.models import SwitchioConfig


class TestBenefitsPasswordResetForm:
    @pytest.fixture(autouse=True)
    def init(self):
        self.form = BenefitsPasswordResetForm()

    def test_recaptcha_mixin(self):
        assert isinstance(self.form, ValidateRecaptchaMixin)


@pytest.mark.django_db
class TestBenefitsSetPasswordForm:
    @pytest.fixture(autouse=True)
    def init(self, model_User):
        self.form = BenefitsSetPasswordForm(model_User)

    def test_recaptcha_mixin(self):
        assert isinstance(self.form, ValidateRecaptchaMixin)


@pytest.mark.django_db
class TestTransitAgencyGroupForm:
    def test_valid(self, model_TransitAgency, model_LittlepayConfig):
        agency2 = TransitAgency.objects.create(
            slug="cst2",
            short_name="TEST",
            long_name="Test Transit Agency",
            info_url="https://example.com/test-agency",
            phone="800-555-5555",
            active=True,
            logo="agencies/cst.png",
        )
        agency2.transit_processor_config = model_LittlepayConfig
        agency2.save()

        agency_list = [model_TransitAgency, agency2]
        form = TransitAgencyGroupForm({"label": "Group", "transit_agencies": agency_list})

        assert form.is_valid()
        assert list(form.cleaned_data["transit_agencies"]) == agency_list

    @pytest.mark.usefixtures("model_LittlepayConfig")
    def test_invalid_if_multiple_processors(self, model_TransitAgency, model_PemData):
        switchio_agency = TransitAgency.objects.create(
            slug="cst2",
            short_name="TEST",
            long_name="Test Transit Agency",
            info_url="https://example.com/test-agency",
            phone="800-555-5555",
            active=True,
            logo="agencies/cst.png",
        )
        # Can't use model_SwitchioConfig here because that applies itself to model_TransitAgency.
        switchio_config = SwitchioConfig.objects.create(
            environment=Environment.DEV,
            tokenization_api_key="api_key",
            tokenization_api_secret_name="apisecret",
        )
        switchio_agency.transit_processor_config = switchio_config
        switchio_agency.save()

        form = TransitAgencyGroupForm({"label": "Group", "transit_agencies": [model_TransitAgency, switchio_agency]})

        assert not form.is_valid()
        assert "Agencies must all use the same transit processor." in form.errors["transit_agencies"]
