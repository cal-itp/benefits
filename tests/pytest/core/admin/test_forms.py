import pytest

from benefits.core.admin.forms import BenefitsPasswordResetForm, BenefitsSetPasswordForm
from benefits.core.mixins import ValidateRecaptchaMixin


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
