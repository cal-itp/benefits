"""
The core application: Helper form widgets.
"""
import copy
from django.forms import widgets


class FormControlTextInput(widgets.TextInput):
    """A styled text input."""

    def __init__(self, pattern=None, placeholder=None, **kwargs):
        super().__init__(**kwargs)

        self.attrs.update({"class": "form-control form-control-lg"})
        if pattern:
            self.attrs.update({"pattern": pattern})
        if placeholder:
            self.attrs.update({"placeholder": placeholder})


class RadioSelect(widgets.RadioSelect):
    template_name = "core/widgets/radio_select.html"
    option_template_name = "core/widgets/radio_select_option.html"

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
        for choice_value, choice_description in self.choice_descriptions:
            if choice_value == value and choice_description is not None:
                option.update({"description": choice_description})

        return option
