# epic:
# https://github.com/orgs/compilerla/projects/6/views/8?pane=issue&itemId=126425767&issue=cal-itp%7Cbenefits%7C3123

# figma designs:
# https://www.figma.com/design/SeSd3LaLd6WkbEYhmtKpO3/Benefits--Full-Application-?node-id=20426-7597

# DONE:
# implement eyebrow text (via inverted headings)
# logo strip (*current* logos)
# implement transit agency <select/> picker on homepage

# TODO:
# yank modal/card code for selecting an agency
# how to sequence updating the logos in production? would we just do that all at once immediately before deploying?

from django import forms


class ChooseAgencyForm(forms.Form):
    # this variable name dictates the #id of the associated div
    # props are supplied in the FormView (to support localization)
    select_transit_agency = forms.ChoiceField()

    def get_eligibility_url(self):
        return self.cleaned_data["select_transit_agency"] + "/eligibility"
