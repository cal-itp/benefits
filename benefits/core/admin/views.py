from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse_lazy

from benefits.core.admin.forms import BenefitsPasswordResetForm, BenefitsSetPasswordForm
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


class BenefitsPasswordResetConfirmView(RecaptchaEnabledMixin, PasswordResetConfirmView):
    """Subclass of stock PasswordResetConfirmView to enable reCAPTCHA and change redirect destination"""

    form_class = BenefitsSetPasswordForm
    success_url = reverse_lazy("admin:login")

    def form_valid(self, form):
        messages.success(self.request, "Your password has been reset. Please log in.")
        return super().form_valid(form)
