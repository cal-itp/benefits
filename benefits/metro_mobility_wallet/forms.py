from django import forms


class TermsAcceptanceForm(forms.Form):
    pass
    # """Form to capture acceptance of program terms."""

    action_url_name = "metro_mobility_wallet:terms"
    id = "form-accept-terms"
    method = "POST"

    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "mmw-terms-checkbox",
            }
        ),
    )


class ContactInfoConfirmationForm(forms.Form):
    pass
