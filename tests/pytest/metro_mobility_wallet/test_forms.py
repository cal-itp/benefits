import pytest

from benefits.core.mixins import ValidateRecaptchaMixin
from benefits.metro_mobility_wallet.forms import ContactInfoConfirmationForm


class TestTermsAcceptanceForm:
    pass


class TestContactInfoConfirmationForm:

    @pytest.fixture(autouse=True)
    def init(self):
        """Initialize the form with valid data for a successful submission test"""

        self.valid_data = {"email": "mail@example.com", "phone_number": "987-654-3210"}
        self.form = ContactInfoConfirmationForm(data=self.valid_data)

    def test_recaptcha_mixin(self):
        assert isinstance(self.form, ValidateRecaptchaMixin)

    def test_base_attributes_initialization(self):
        """Ensure the base form initializes fields even when attributes are None."""

        # Should have the fields defined in the base __init__
        assert "email" in self.form.fields
        assert "phone_number" in self.form.fields

        # Check that attributes that are None/not set do not cause errors
        email_widget_attrs = self.form.fields["email"].widget.attrs
        assert email_widget_attrs.get("pattern") is None
        assert email_widget_attrs.get("placeholder") is None
        assert email_widget_attrs.get("novalidate") is None
        phone_widget_attrs = self.form.fields["phone_number"].widget.attrs
        assert phone_widget_attrs.get("placeholder") is None
        assert phone_widget_attrs.get("novalidate") is None

        # The base class sets name_custom_validity by default
        assert hasattr(self.form, "use_custom_validity")

    def test_valid_data_and_widget_attributes(self):
        """Test happy path validation and ensure required HTML widget attributes are present."""

        assert self.form.is_valid()

        # no custom attributes for the email widget

        # Phone widget
        phone_widget_attrs = self.form.fields["phone_number"].widget.attrs
        assert phone_widget_attrs["pattern"] == self.form.us_phone_pattern_js

        assert self.form.use_custom_validity

    def test_invalid_data(self):
        """Test failure cases for ContactInfoConfirmationForm (too long, non-numeric)."""

        # Invalid email format
        form_bad_email = ContactInfoConfirmationForm(data={"email": "mail@example", "phone_number": "987-654-3210"})
        assert not form_bad_email.is_valid()

        # Invalid phone format
        form_bad_phone = ContactInfoConfirmationForm(data={"email": "mail@example.com", "phone_number": "abc-123-@#$%"})
        assert not form_bad_phone.is_valid()
