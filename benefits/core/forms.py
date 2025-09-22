from django import forms

# from . import models

DUMMY_CHOICES = [
    ("", "Choose your transit provider now"),
    ("cst", "CA state transit agency"),
]


def get_active_agency_names():
    # TODO: pull slugs and long names from active_agencies
    return DUMMY_CHOICES


class ChooseAgencyForm(forms.Form):
    enroll = forms.ChoiceField(
        choices=get_active_agency_names,
        required=True,
        widget=forms.Select,
    )

    def get_slug(self):
        return self.cleaned_data["enroll"]
