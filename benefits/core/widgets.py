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


class VerifierRadioSelect(widgets.RadioSelect):
    """A radio select input styled for the Eligibility Verifier"""

    template_name = "core/widgets/verifier-radio-select.html"
    option_template_name = "core/widgets/verifier-radio-select-option.html"

    def __init__(self, selection_label_templates=(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection_label_templates = list(selection_label_templates)

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.selection_label_templates = copy.copy(self.selection_label_templates)
        return obj

    def create_option(self, name, value, label, selected, index, subindex, attrs):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        # this implementation does not support groups from ChoiceWidget.optgroups
        if value in self.selection_label_templates:
            option.update({"selection_label_template": self.selection_label_templates[value]})

        return option
