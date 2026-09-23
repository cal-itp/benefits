import logging

logger = logging.getLogger(__name__)


class TransitProcessorRegistry:
    """Registry which stores information about all registered TransitProcessor modules."""

    entries = []

    @classmethod
    def add(cls, system_name):
        cls.entries.append(system_name)
        logger.debug(f'Registered "{system_name}" as a transit processor')
        logger.debug(f"Currently registered transit processors: {cls.entries}")

    @classmethod
    def get_transit_processor_config(cls, transit_agency):
        if transit_agency.transit_processor_config:
            for system_name in cls.entries:
                config_model_name = system_name + "config"
                if hasattr(transit_agency.transit_processor_config, config_model_name):
                    transit_processor_config = getattr(transit_agency.transit_processor_config, config_model_name)
                else:
                    transit_processor_config = None

                if transit_processor_config:
                    return transit_processor_config

            return None
        return None
