from django import template

register = template.Library()


@register.inclusion_tag('rijkshuisstijl/components/form/form.html', takes_context=True)
def form(context, form, label='', **kwargs):
    kwargs['request'] = context['request']
    kwargs['form'] = form
    kwargs['label'] = label
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/form/input.html')
def form_input(**kwargs):
    return kwargs
