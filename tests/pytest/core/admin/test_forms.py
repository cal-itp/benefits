import pytest
from django.forms import ValidationError

from benefits.core.admin.forms import BenefitsPasswordResetForm


@pytest.mark.django_db
def test_benefits_password_reset_form_recaptcha_fail(app_request, mocker):
    mocker.patch("benefits.core.recaptcha.verify", return_value=False)
    form = BenefitsPasswordResetForm(data={"email": "mail@example.com"})

    with pytest.raises(ValidationError):
        form.clean()
