from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

from benefits.core.mixins import ValidateRecaptchaMixin
from benefits.core.models import TransitAgencyGroup


class BenefitsPasswordResetForm(ValidateRecaptchaMixin, PasswordResetForm):
    pass


class BenefitsSetPasswordForm(ValidateRecaptchaMixin, SetPasswordForm):
    pass


class TransitAgencyGroupForm(forms.ModelForm):
    class Meta:
        model = TransitAgencyGroup
        fields = ["label", "transit_agencies"]

    def clean_transit_agencies(self):
        """Check selected agencies for different transit processors.

        This cannot be done in the model's clean() because of how
        ManyToMany relationships are added after initial object creation.
        """
        if transit_agencies := self.cleaned_data.get("transit_agencies"):
            transit_processors = set(agency.transit_processor for agency in transit_agencies)

            if len(transit_processors) > 1:
                raise forms.ValidationError("Agencies must all use the same transit processor.")

        return transit_agencies
