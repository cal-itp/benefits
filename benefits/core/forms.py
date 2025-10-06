# TODO:
# yank modal/card code for selecting an agency

from django import forms
from django.utils.translation import gettext_lazy as _

from benefits.core import models


# better to pull info like this out of context instead?
def get_active_agency_names(placeholder="placeholder"):
    agency_names = [(None, placeholder)]
    for a in models.TransitAgency.all_active():
        agency_names.append((a.slug, a.long_name))

    return agency_names


class ChooseAgencyForm(forms.Form):
    id = "form-agency-selection"
    method = "POST"

    select_transit_agency = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholder = _("Choose your transit provider")
        self.fields["select_transit_agency"] = forms.ChoiceField(
            choices=get_active_agency_names(placeholder),
            label=_("Enroll today"),
            label_suffix="",
            required=True,
            widget=forms.Select(
                attrs={
                    "class": "form-select",
                    "aria-label": placeholder,
                    "data-custom-validity": _("Please choose a transit provider."),
                }
            ),
        )
        self.use_custom_validity = True

    def get_eligibility_url(self):
        return self.cleaned_data["select_transit_agency"] + "/eligibility"
