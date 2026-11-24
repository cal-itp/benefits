"""
The core application: Helper form widgets.
"""

import copy

from django.forms import widgets


class FormControlMixin:
    """Mixin to apply customizations to Django form widgets.

    Applies class="form-control" always, and pattern and placeholder attributes, if passed.
    """

    def __init__(self, pattern=None, placeholder=None, novalidate=False, **kwargs):
        super().__init__(**kwargs)

        self.attrs.update({"class": "form-control"})
        if pattern:
            self.attrs.update({"pattern": pattern})
        if placeholder:
            self.attrs.update({"placeholder": placeholder})
        if novalidate:
            self.attrs.update({"novalidate": True})


class FormControlTextInput(FormControlMixin, widgets.TextInput):
    """Customized Django TextInput widget that renders as <input type="text" … >."""


class FormControlEmailInput(FormControlMixin, widgets.EmailInput):
    """Customized Django EmailInput widget that renders as <input type="email" … >."""


class FormControlTelInput(FormControlMixin, widgets.TelInput):
    """Customized Django TelInput widget that renders as <input type="tel" … >."""


class FlowRadioSelect(widgets.RadioSelect):
    """A radio select input styled for the Enrollment Flow."""

    template_name = "core/widgets/flow-radio-select.html"
    option_template_name = "core/widgets/flow-radio-select-option.html"

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
