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
