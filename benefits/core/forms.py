from django import forms
from django.utils.translation import gettext_lazy as _

from benefits.core import models


def get_active_agency_choices(placeholder="placeholder"):
    agency_names = [(None, placeholder)]
    for a in models.TransitAgency.all_active():
        agency_names.append((a.slug, a.long_name))

    return agency_names


class AgencySelectWidget(forms.Select):
    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)

        if value:
            option["attrs"]["data-short-name"] = models.TransitAgency.by_slug(value).short_name
        return option


class ChooseAgencyForm(forms.Form):
    """Form to select the agency to request transit benefits for."""

    id = "form-agency-selection"
    method = "POST"

    select_transit_agency = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholder = _("Choose your transit provider")
        self.classes = "pt-lg-5 pt-8"
        self.fields["select_transit_agency"] = forms.ChoiceField(
            choices=get_active_agency_choices(placeholder),
            label=_("Enroll today"),
            label_suffix="",
            required=True,
            widget=AgencySelectWidget(
                attrs={
                    "class": "form-select",
                    "aria-label": placeholder,
                    "data-custom-validity": _("Please choose a transit provider."),
                }
            ),
        )
        self.use_custom_validity = True

    def clean(self):
        cleaned_data = super().clean()
        agency_slug = cleaned_data.get("select_transit_agency")
        if agency_slug:
            self.selected_transit_agency = models.TransitAgency.by_slug(agency_slug)

        return cleaned_data
