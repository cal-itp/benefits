import pytest

from benefits.enrollment.registry import TransitProcessorRegistry
from benefits.enrollment_littlepay.models import LittlepayConfig


@pytest.mark.django_db
class TestTransitProcessorAppRegistry:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.system_name = "littlepay"

    def test_add(self):
        TransitProcessorRegistry.add(self.system_name)

        assert self.system_name in TransitProcessorRegistry.entries

    def test_get_transit_processor_config(self, model_TransitAgency, model_LittlepayConfig):
        model_TransitAgency.transit_processor_config = model_LittlepayConfig
        model_TransitAgency.save()

        config = TransitProcessorRegistry.get_transit_processor_config(model_TransitAgency)
        assert isinstance(config, LittlepayConfig)
        assert config == model_TransitAgency.transit_processor

    def test_get_transit_processor_config_for(self, model_TransitAgency, model_LittlepayConfig):
        model_TransitAgency.transit_processor_config = model_LittlepayConfig
        model_TransitAgency.save()

        config = TransitProcessorRegistry.get_transit_processor_config_for(
            transit_agency=model_TransitAgency,
            system_name=self.system_name,
        )
        assert isinstance(config, LittlepayConfig)
        assert config == model_TransitAgency.transit_processor
