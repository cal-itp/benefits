"""
The core application: Helper form widgets.
"""
import copy
from django.forms import widgets


class FormControlTextInput(widgets.TextInput):
    """A styled text input."""

    def __init__(self, pattern=None, placeholder=None, **kwargs):
        super().__init__(**kwargs)

        self.attrs.update({"class": "form-control"})
        if pattern:
            self.attrs.update({"pattern": pattern})
        if placeholder:
            self.attrs.update({"placeholder": placeholder})


class RadioSelect(widgets.RadioSelect):
    template_name = "core/widgets/verifier_radio_select.html"
    option_template_name = "core/widgets/verifier_radio_select_option.html"
    # Note: the templates are specific to the Eligibility Verifier

    def __init__(self, choice_descriptions=(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choice_descriptions = list(choice_descriptions)

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.choice_descriptions = copy.copy(self.choice_descriptions)
        return obj

    def create_option(self, name, value, label, selected, index, subindex, attrs):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        # this implementation does not support groups from ChoiceWidget.optgroups
        if value in self.choice_descriptions:
            option.update({"description": self.choice_descriptions[value]})

        return option
