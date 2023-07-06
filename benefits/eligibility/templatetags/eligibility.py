from django import template


register = template.Library()


@register.inclusion_tag("eligibility/tags/media_item__idcardcheck__mst_cc.html")
def media_item__idcardcheck__mst_cc():
    return {}
