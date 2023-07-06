from django import template


register = template.Library()


@register.inclusion_tag("eligibility/tags/media_item__bankcardcheck.html")
def media_item__bankcardcheck():
    return {}


@register.inclusion_tag("eligibility/tags/media_item__idcardcheck__login_gov.html")
def media_item__idcardcheck__login_gov():
    return {}


@register.inclusion_tag("eligibility/tags/media_item__idcardcheck__mst_cc.html")
def media_item__idcardcheck__mst_cc():
    return {}


@register.inclusion_tag("eligibility/tags/media_item__idcardcheck__veteran.html")
def media_item__idcardcheck__veteran():
    return {}
