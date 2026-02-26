import pytest

from benefits.core import models
from benefits.core.mixins import ValidateRecaptchaMixin
from benefits.eligibility.forms import (
    EligibilityVerificationForm,
    EnrollmentFlowSelectionForm,
    MSTCourtesyCard,
    SBMTDMobilityPass,
)


@pytest.mark.django_db
class TestEnrollmentFlowSelectionForm:
    @pytest.fixture(autouse=True)
    def init(self, model_TransitAgency):
        self.digital = models.EnrollmentFlow.objects.create(
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL],
            label="Digital",
        )
        self.in_person = models.EnrollmentFlow.objects.create(
            supported_enrollment_methods=[models.EnrollmentMethods.IN_PERSON],
            label="In-Person",
        )
        self.both = models.EnrollmentFlow.objects.create(
            supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
            label="Both",
        )
        model_TransitAgency.enrollment_flows.set([self.digital, self.in_person, self.both])
        model_TransitAgency.save()
        self.form = EnrollmentFlowSelectionForm(agency=model_TransitAgency)

    def test_recaptcha_mixin(self):
        assert isinstance(self.form, ValidateRecaptchaMixin)

    def test_filtering_flows(self):
        """Ensures the form only shows flows supporting DIGITAL enrollment."""
        filtered_flow_ids = [choice[0] for choice in self.form.fields["flow"].choices]

        expected_ids = {self.digital.id, self.both.id}
        actual_ids = set(filtered_flow_ids)

        assert expected_ids.issubset(actual_ids)
        assert actual_ids.issubset(expected_ids)


class TestEligibilityVerificationForm:
    @pytest.fixture(autouse=True)
    def init(self):
        self.form = EligibilityVerificationForm()

    def test_recaptcha_mixin(self):
        assert isinstance(self.form, EligibilityVerificationForm)
        assert isinstance(self.form, ValidateRecaptchaMixin)

    def test_base_attributes_initialization(self):
        """Ensure the base form initializes fields even when attributes are None."""
        # Should have the fields defined in the base __init__
        assert "sub" in self.form.fields
        assert "name" in self.form.fields

        # Check that attributes that are None/not set do not cause errors
        assert self.form.fields["sub"].widget.attrs.get("pattern") is None

        # The base class sets name_custom_validity by default
        assert hasattr(self.form, "use_custom_validity")


class TestMSTCourtesyCard:
    """Tests related to the MSTCourtesyCard form."""

    @pytest.fixture(autouse=True)
    def init(self):
        # Initialize the form with valid data for a successful submission test
        self.valid_data = {"sub": "12345", "name": "Gonzalez"}
        self.form = MSTCourtesyCard(data=self.valid_data)

    def test_valid_data_and_widget_attributes(self):
        """Test happy path validation and ensure required HTML widget attributes are present."""
        assert self.form.is_valid()

        sub_attrs = self.form.fields["sub"].widget.attrs
        assert sub_attrs["pattern"] == r"\d{5}"
        assert sub_attrs["inputmode"] == "numeric"
        assert sub_attrs["maxlength"] == "5"
        assert sub_attrs["data-custom-validity"] == "Please enter a 5-digit number."

        name_attrs = self.form.fields["name"].widget.attrs
        assert name_attrs["maxlength"] == "255"
        assert name_attrs["data-custom-validity"] == "Please enter your last name."

        assert self.form.use_custom_validity

    def test_invalid_data(self):
        """Test failure cases for MSTCourtesyCard (too long, non-numeric)."""
        # Too long (6 digits)
        form_long = MSTCourtesyCard(data={"sub": "123456", "name": "Gonzalez"})
        assert not form_long.is_valid()

        # Non-numeric
        form_alpha = MSTCourtesyCard(data={"sub": "abcde", "name": "Gonzalez"})
        assert not form_alpha.is_valid()


class TestSBMTDMobilityPass:
    """Tests related to the SBMTDMobilityPass form."""

    @pytest.fixture(autouse=True)
    def init(self):
        # Initialize with data that covers the 4 or 5 digit pattern
        self.valid_data_4 = {"sub": "1234", "name": "Barbara"}
        self.valid_data_5 = {"sub": "12345", "name": "Barbara"}
        self.form_4 = SBMTDMobilityPass(data=self.valid_data_4)
        self.form_5 = SBMTDMobilityPass(data=self.valid_data_5)

    def test_valid_data_and_widget_attributes(self):
        """Test valid 4- and 5-digit inputs and ensure widget attributes are correct."""
        assert self.form_4.is_valid()
        assert self.form_5.is_valid()

        # Use the 5-digit form instance to check widget attributes
        sub_attrs = self.form_5.fields["sub"].widget.attrs
        assert sub_attrs["pattern"] == r"\d{4,5}"
        assert sub_attrs["maxlength"] == "5"
        assert sub_attrs["inputmode"] == "numeric"
        assert sub_attrs["data-custom-validity"] == "Please enter a 4- or 5-digit number."

        name_attrs = self.form_5.fields["name"].widget.attrs
        assert name_attrs["maxlength"] == "255"
        assert name_attrs["data-custom-validity"] == "Please enter your last name."

        assert self.form_5.use_custom_validity

    def test_invalid_data(self):
        """Test failure cases for SBMTDMobilityPass (too short, too long, non-numeric)."""
        # Too short (3 digits)
        form_short = SBMTDMobilityPass(data={"sub": "123", "name": "Barbara"})
        assert not form_short.is_valid()

        # Too long (6 digits)
        form_long = SBMTDMobilityPass(data={"sub": "123456", "name": "Barbara"})
        assert not form_long.is_valid()

        # Non-numeric 5-digits
        form_alpha = SBMTDMobilityPass(data={"sub": "abcde", "name": "Barbara"})
        assert not form_alpha.is_valid()
