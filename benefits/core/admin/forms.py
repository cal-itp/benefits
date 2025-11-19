from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

from benefits.core.mixins import ValidateRecaptchaMixin


class BenefitsPasswordResetForm(ValidateRecaptchaMixin, PasswordResetForm):
    pass


class BenefitsSetPasswordForm(ValidateRecaptchaMixin, SetPasswordForm):
    pass
