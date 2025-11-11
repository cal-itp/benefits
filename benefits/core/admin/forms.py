from django.contrib.auth.forms import PasswordResetForm
from django.forms import ValidationError

from benefits.core import recaptcha


class BenefitsPasswordResetForm(PasswordResetForm):

    def clean(self):
        if not recaptcha.verify(self.data):
            raise ValidationError("reCAPTCHA failed, please try again.")
        return super().clean()
