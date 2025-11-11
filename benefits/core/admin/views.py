from django.contrib.auth.views import PasswordResetView

from benefits.core.admin.forms import BenefitsPasswordResetForm
from benefits.core.mixins import RecaptchaEnabledMixin


class BenefitsPasswordResetView(RecaptchaEnabledMixin, PasswordResetView):
    form_class = BenefitsPasswordResetForm
