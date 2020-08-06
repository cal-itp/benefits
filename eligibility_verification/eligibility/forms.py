from django import forms


class EligibilityVerificationForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(help_text="We use this to confirm your driver license number")
    identification = forms.RegexField("[A-Z][0-9]{7}", label="CA Driver License or ID Card number")
