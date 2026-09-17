class TransitProcessorRegistry:
    """Singleton which stores information about all registered TransitProcessor modules."""

    entries = {}

    def add(self, system_name, module_name):
        self.entries.setdefault(system_name, {})
        self.entries.get(system_name).update(dict(module_name=module_name))
