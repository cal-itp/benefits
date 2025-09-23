from django import forms

# from . import models

# TODO:
# add translations
# yank old 'call to action' code
# pull slugs and long names from active_agencies
# ??

PLACEHOLDER = "Choose your transit provider"
DUMMY_CHOICES = [
    (None, PLACEHOLDER),
    ("cst", "California State Transit"),
]


def get_active_agency_names():
    return DUMMY_CHOICES


class ChooseAgencyForm(forms.Form):

    enroll = forms.ChoiceField(
        choices=get_active_agency_names,
        label="Enroll today",
        label_suffix="",
        required=True,
        # csrf doesnt allow this. might be a bad idea regardless
        # attrs={"onchange": "function () { console.log('hi!') };"}
        widget=forms.Select(attrs={"class": "form-select", "aria-label": PLACEHOLDER}),
    )

    def get_slug(self):
        return self.cleaned_data["enroll"]
