import pytest

from benefits.enrollment.registry import TransitProcessorRegistry
from benefits.enrollment_littlepay.models import LittlepayConfig


def test_TransitProcessorRegistry_add():
    system_name = "acme"
    TransitProcessorRegistry.add(system_name)

    assert system_name in TransitProcessorRegistry.entries


@pytest.mark.django_db
def test_TransitProcessorRegistry_get_transit_processor_config(model_TransitAgency, model_LittlepayConfig):
    model_TransitAgency.transit_processor_config = model_LittlepayConfig
    model_TransitAgency.save()

    system_name = "littlepay"
    TransitProcessorRegistry.add(system_name=system_name)

    config = TransitProcessorRegistry.get_transit_processor_config(model_TransitAgency)
    assert isinstance(config, LittlepayConfig)
    assert config == model_TransitAgency.transit_processor


@pytest.mark.django_db
def test_TransitProcessorRegistry_get_transit_processor_config_for(model_TransitAgency, model_LittlepayConfig):
    model_TransitAgency.transit_processor_config = model_LittlepayConfig
    model_TransitAgency.save()

    system_name = "littlepay"
    TransitProcessorRegistry.add(system_name=system_name)

    config = TransitProcessorRegistry.get_transit_processor_config_for(
        transit_agency=model_TransitAgency,
        system_name=system_name,
    )
    assert isinstance(config, LittlepayConfig)
    assert config == model_TransitAgency.transit_processor
