from django.contrib.auth.views import PasswordResetView

from benefits.core.mixins import RecaptchaEnabledMixin


class BenefitsPasswordResetView(RecaptchaEnabledMixin, PasswordResetView):
    pass
