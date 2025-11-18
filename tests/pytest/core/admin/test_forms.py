import pytest
from django.forms import ValidationError

from benefits.core.admin.forms import BenefitsPasswordResetForm, BenefitsSetPasswordForm


@pytest.mark.django_db
def test_benefits_password_reset_form_recaptcha_fail(app_request, mocker):
    mocker.patch("benefits.core.recaptcha.verify", return_value=False)
    form = BenefitsPasswordResetForm(data={"email": "mail@example.com"})

    with pytest.raises(ValidationError):
        form.clean()


@pytest.mark.django_db
def test_benefits_set_password_form_recaptcha_fail(app_request, mocker, model_User):
    mocker.patch("benefits.core.recaptcha.verify", return_value=False)
    form = BenefitsSetPasswordForm(model_User, data={"new_password1": "test123", "new_password2": "test123"})

    with pytest.raises(ValidationError):
        form.clean()
