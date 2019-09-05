from uuid import uuid4

from django import template

register = template.Library()


@register.inclusion_tag('rijkshuisstijl/components/button/button.html')
def button(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/filter/filter.html')
def dom_filter(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/datagrid/datagrid.html')
def datagrid(**kwargs):
    kwargs['id'] = kwargs.get('id', 'datagrid-' + str(uuid4()))
    kwargs['object_list'] = kwargs.get('object_list', kwargs['queryset'])

    for key in ('columns', 'column_values', 'modifier_mapping'):
        try:
            kwargs[key] = kwargs[key].split(',')
        except (AttributeError, KeyError):
            pass

    if kwargs['modifier_key']:
        modifier_map = {}

        if kwargs['modifier_mapping']:
            for mapping in kwargs['modifier_mapping']:
                mapping = mapping.split(':')
                modifier_map[mapping[0].strip()] = mapping[1].strip()

            key = kwargs['modifier_key']

        for object in kwargs['queryset']:
            modifier_value = getattr(object, key)
            try:
                modifier_value = modifier_map[modifier_value]
            except KeyError:
                pass

            object.modifier_class = modifier_value

    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/button/link.html')
def button_link(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/footer/footer.html', takes_context=True)
def footer(context, **kwargs):
    kwargs['request'] = context['request']
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/header/header.html')
def header(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/icon/icon.html')
def icon(icon, **kwargs):
    kwargs['icon'] = icon
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/image/image.html')
def image(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/login-bar/login-bar.html', takes_context=True)
def login_bar(context, **kwargs):
    kwargs['request'] = context['request']
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/logo/logo.html')
def logo(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/meta/meta-css.html')
def meta_css(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/meta/meta-js.html')
def meta_js(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/meta/meta-icons.html')
def meta_icons(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/navigation-bar/navigation-bar.html', takes_context=True)
def navigation_bar(context, **kwargs):
    kwargs['request'] = context['request']
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/paginator/paginator.html', takes_context=True)
def paginator(context):
    return context


@register.inclusion_tag('rijkshuisstijl/components/search/search.html')
def search(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/skiplink/skiplink.html')
def skiplink(**kwargs):
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/skiplink/skiplink-target.html')
def skiplink_target(**kwargs):
    return kwargs
