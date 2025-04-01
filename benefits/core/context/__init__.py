from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy

from .agency import AgencySlug, agency_index
from .flow import FlowHelp, SystemName, flows_help


def formatted_gettext_lazy(string, *args, **kwargs):
    """Wraps format_lazy around gettext_lazy for simpler calling."""
    return format_lazy(gettext_lazy(string), *args, **kwargs)


__all__ = ["AgencySlug", "FlowHelp", "SystemName", "agency_index", "flows_help", "formatted_gettext_lazy"]
