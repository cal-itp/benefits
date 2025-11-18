from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.urls import reverse_lazy

from benefits.core.admin.forms import BenefitsPasswordResetForm
from benefits.core.mixins import RecaptchaEnabledMixin


class BenefitsPasswordResetView(RecaptchaEnabledMixin, PasswordResetView):
    """Subclass of stock PasswordResetView to enable reCAPTCHA and pass email to done view"""

    form_class = BenefitsPasswordResetForm

    def form_valid(self, form):
        self.success_url = f"{reverse_lazy("password_reset_done")}?email={form.cleaned_data["email"]}"
        return super().form_valid(form)


class BenefitsPasswordResetDoneView(PasswordResetDoneView):
    """Subclass of stock PasswordResetDoneView to receive email param and add to template context"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.request.GET.get("email")
        return context
