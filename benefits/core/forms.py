# epic:
# https://github.com/orgs/compilerla/projects/6/views/8?pane=issue&itemId=126425767&issue=cal-itp%7Cbenefits%7C3123

# figma designs:
# https://www.figma.com/design/SeSd3LaLd6WkbEYhmtKpO3/Benefits--Full-Application-?node-id=20426-7597

# DONE:
# rough cut at a logo strip (using *current* logos)
# rough cut at inverting headings to implement eyebrow text
# add <select/> to homepage to list active agencies in a dropdown
# wire up submit of form to appropriate agencies eligibility landing page
# wire up interstitial navigation onchange of <select/> to the agency specific landing page

# TODO:
# hydrate the <select/> from active_agencies instead of hard-coding slugs and long names here
# figure out how to size logos in the new logo strip dynamically
# verify that the current <select/> change handler isnt an anti-pattern
# ensure heading text doesnt shift vertically when an agency is selected from the dropdown
# add translations
# yank old 'call to action' code
# how to sequence updating the logos in production? would we just do that all at once immediately before deploying?
# ??

from django import forms

# from . import models

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
