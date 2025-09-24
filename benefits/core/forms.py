# epic:
# https://github.com/orgs/compilerla/projects/6/views/8?pane=issue&itemId=126425767&issue=cal-itp%7Cbenefits%7C3123

# figma designs:
# https://www.figma.com/design/SeSd3LaLd6WkbEYhmtKpO3/Benefits--Full-Application-?node-id=20426-7597

# DONE:
# implement eyebrow text (via inverted headings)
# logo strip (*current* logos)
# implement transit agency <select/> picker on homepage

# TODO:
# add translations
# yank modal/card code for selecting an agency
# how to sequence updating the logos in production? would we just do that all at once immediately before deploying?
# ??

from django import forms

from . import models

PLACEHOLDER = "Choose your transit provider"


def get_active_agency_names():
    agency_names = [(None, PLACEHOLDER)]
    for a in models.TransitAgency.all_active():
        agency_names.append((a.slug, a.long_name))

    return agency_names


class ChooseAgencyForm(forms.Form):
    # this variable name dictates the #id of the associated div
    select_transit_agency = forms.ChoiceField(
        choices=get_active_agency_names,
        label="Enroll today",
        label_suffix="",
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "aria-label": PLACEHOLDER}),
    )

    def get_eligibility_url(self):
        return self.cleaned_data["select_transit_agency"] + "/eligibility"
