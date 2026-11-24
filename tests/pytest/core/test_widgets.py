from django import forms

from benefits.core.widgets import FormControlEmailInput, FormControlMixin, FormControlTelInput, FormControlTextInput


class TestFormControlMixin:
    class SampleFormControl(FormControlMixin, forms.widgets.TextInput):
        pass

    def test_init(self):
        form = forms.Form()
        form.test_field = forms.CharField(widget=self.SampleFormControl())
        widget = form.test_field.widget

        assert widget.attrs["class"] == "form-control"
        assert 'class="form-control"' in widget.render(name="test", value="")

    def test_init_with_pattern(self):
        form = forms.Form()
        form.test_field = forms.CharField(widget=self.SampleFormControl(pattern=r"regex"))
        widget = form.test_field.widget

        assert widget.attrs["class"] == "form-control"
        assert widget.attrs["pattern"] == r"regex"
        assert 'pattern="regex"' in widget.render(name="test", value="")

    def test_init_with_placeholder(self):
        form = forms.Form()
        form.test_field = forms.CharField(widget=self.SampleFormControl(placeholder="placeholder"))
        widget = form.test_field.widget

        assert widget.attrs["class"] == "form-control"
        assert widget.attrs["placeholder"] == "placeholder"
        assert 'placeholder="placeholder"' in widget.render(name="test", value="")

    def test_init_with_novalidate(self):
        form = forms.Form()
        form.test_field = forms.CharField(widget=self.SampleFormControl(novalidate=True))
        widget = form.test_field.widget

        assert widget.attrs["class"] == "form-control"
        assert widget.attrs["novalidate"] is True
        assert "novalidate" in widget.render(name="test", value="")

    def test_subclasses(self):
        form = forms.Form()
        form.email_field = forms.CharField(widget=FormControlEmailInput())
        email_widget = form.email_field.widget
        form.phone_field = forms.CharField(widget=FormControlTelInput())
        phone_widget = form.phone_field.widget
        form.text_field = forms.CharField(widget=FormControlTextInput())
        text_widget = form.text_field.widget

        assert isinstance(form.email_field.widget, forms.widgets.EmailInput)
        assert 'type="email"' in email_widget.render(name="test", value="")
        assert isinstance(form.phone_field.widget, forms.widgets.TelInput)
        assert 'type="tel"' in phone_widget.render(name="test", value="")
        assert isinstance(form.text_field.widget, forms.widgets.TextInput)
        assert 'type="text"' in text_widget.render(name="test", value="")
