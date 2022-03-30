"""
The core application: Helper form widgets.
"""
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
