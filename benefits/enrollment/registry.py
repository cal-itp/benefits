import logging

logger = logging.getLogger(__name__)


class TransitProcessorRegistry:
    """Registry which stores information about all registered TransitProcessor modules."""

    entries = {}

    def add(self, system_name, module_name):
        self.entries.setdefault(system_name, {})
        self.entries.get(system_name).update(dict(module_name=module_name))

        logger.debug(f'Registered "{system_name}" as a transit processor')
        logger.debug(f"Currently registered transit processors: {list(self.entries.keys())}")


# helper methods


def get_transit_processor_config(transit_agency):
    if transit_agency.transit_processor_config:
        from django.apps import apps

        from benefits.enrollment.apps import EnrollmentAppConfig

        enrollment_app_config = apps.get_app_config(EnrollmentAppConfig.label)
        registry = enrollment_app_config.transit_processors

        for system_name in registry.entries:
            transit_processor_config = get_transit_processor_config_for(transit_agency, system_name)
            if transit_processor_config:
                return transit_processor_config

        return None


def get_transit_processor_config_for(transit_agency, system_name):
    config_model_name = system_name + "config"
    if hasattr(transit_agency.transit_processor_config, config_model_name):
        return getattr(transit_agency.transit_processor_config, config_model_name)
    else:
        return None
