#
#   All template tags provided by the PSU Base plugin are registered in this file.
#   For browse-ability, all processing happens outside this file.
#

from django import template
from psu_base.classes.Log import Log
from psu_base.services import utility_service, auth_service
from psu_base.templatetags.tag_processing import supporting_functions as support, html_generating, static_content
from psu_base.classes.User import User

register = template.Library()
log = Log()


# # # # # # # # # # # # # # # # # # #
# UTILITY CATEGORY
# # # # # # # # # # # # # # # # # # #


@register.simple_tag()
def app_code():
    return utility_service.get_app_code()


@register.simple_tag()
def app_name():
    return utility_service.get_app_name()


@register.simple_tag()
def app_version():
    return utility_service.get_app_version()


@register.simple_tag()
def psu_version():
    return utility_service.get_setting('PSU_BASE_VERSION')


@register.simple_tag(takes_context=True)
def setting_value(context, *args, **kwargs):
    return utility_service.get_setting(args[1])


@register.simple_tag(takes_context=True)
def set_var(context, *args, **kwargs):
    log.trace(args)
    context[args[0]] = args[1]
    return ''


@register.tag()
def if_production(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = utility_service.is_production()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_non_production(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = utility_service.is_non_production()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_feature_enabled(parser, token):
    tag_name, feature_code = token.split_contents()
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = utility_service.feature_is_enabled(feature_code)
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_feature_disabled(parser, token):
    tag_name, feature_code = token.split_contents()
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = not utility_service.feature_is_enabled(feature_code)
    return support.ConditionalResponseNode(nodelist, result)


# # # # # # # # # # # # # # # # # # #
# AUTHENTICATION CATEGORY
# # # # # # # # # # # # # # # # # # #


@register.tag()
def if_logged_in(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = auth_service.is_logged_in()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_not_logged_in(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = not auth_service.is_logged_in()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_can_impersonate(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = auth_service.get_auth_object().can_impersonate()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_can_not_impersonate(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = not auth_service.get_auth_object().can_impersonate()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_impersonating(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = auth_service.get_auth_object().is_impersonating()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_not_impersonating(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = not auth_service.get_auth_object().is_impersonating()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_proxying(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = auth_service.get_auth_object().is_proxying()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_not_proxying(parser, token=None):
    tag_name = token.split_contents()[0]
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = not auth_service.get_auth_object().is_proxying()
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_has_authority(parser, token):
    tag_name, authority_code = token.split_contents()
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = auth_service.has_authority(authority_code)
    return support.ConditionalResponseNode(nodelist, result)


@register.tag()
def if_not_has_authority(parser, token):
    tag_name, authority_code = token.split_contents()
    nodelist = parser.parse((f"end_{tag_name}",))
    parser.delete_first_token()
    result = not auth_service.has_authority(authority_code)
    return support.ConditionalResponseNode(nodelist, result)


@register.simple_tag(takes_context=True)
def set_auth_object(context):
    context['auth_object'] = auth_service.get_auth_object()
    return ''


@register.simple_tag(takes_context=True)
def set_current_user(context):
    context['current_user'] = auth_service.get_user()
    return ''


@register.simple_tag(takes_context=True)
def display_name(context):
    return auth_service.get_user().display_name


# # # # # # # # # # # # # # # # # # #
# STATIC CONTENT CATEGORY
# # # # # # # # # # # # # # # # # # #


@register.simple_tag
def static_content_url():
    return utility_service.get_static_content_url()


@register.simple_tag
def wdt_content_url(*args, **kwargs):
    return static_content.wdt_url(kwargs.get('version'))


@register.simple_tag
def jquery(*args, **kwargs):
    return static_content.jquery(*args, **kwargs)


@register.simple_tag
def bootstrap(*args, **kwargs):
    return static_content.bootstrap(*args, **kwargs)


@register.simple_tag
def font_awesome(*args, **kwargs):
    return static_content.font_awesome(*args, **kwargs)


@register.simple_tag
def wdt_stylesheet(css_file, version=None):
    return static_content.wdt_stylesheet(css_file, version)


@register.simple_tag
def wdt_javascript(js_file, version=None):
    return static_content.wdt_javascript(js_file, version)


@register.tag()
def image(parser, token):
    return html_generating.ImageNode(token.split_contents())


# # # # # # # # # # # # # # # # # # #
# HTML-GENERATING CATEGORY
# # # # # # # # # # # # # # # # # # #


@register.inclusion_tag('template_components/pagination.html')
def pagination(paginated_results):
    """Example: {%pagination polls%}"""
    return html_generating.pagination(paginated_results)


@register.tag()
def fa(parser, token):
    """Render a screen-reader-friendly FontAwesome4 icon"""
    return html_generating.FaNode(token.split_contents())


@register.tag()
def select_menu(parser, token):
    return html_generating.SelectNode(token.split_contents())


@register.tag()
def id_photo(parser, token):
    """Example: {%id_photo user="mjg"%} or {%id_photo user=user_instance%} """
    return html_generating.PhotoNode(token.split_contents())


@register.inclusion_tag('template_components/id_tag.html')
def id_tag(user_instance_or_info):
    """Example: {%id_tag "mjg"%} or {%id_card user_instance%} """
    return {'user_instance': User(user_instance_or_info)}


@register.inclusion_tag('template_components/id_card.html')
def id_card(user_instance_or_info):
    """Example: {%id_card user="mjg"%} or {%id_card user=user_instance%} """
    return {'user_instance': User(user_instance_or_info)}


# # # # # # # # # # # # # # # # # # #
# UNLIKELY TO BE RE-USED CATEGORY
# # # # # # # # # # # # # # # # # # #


@register.inclusion_tag('template_components/developer_menu.html')
def developer_menu():
    pass


@register.inclusion_tag('template_components/sso_menu.html')
def sso_menu():
    pass


@register.inclusion_tag('template_components/admin_script.html', takes_context=True)
def admin_script(context):
    return {'scripts': utility_service.get_admin_scripts(context.request, auth_service.get_user().username)}
