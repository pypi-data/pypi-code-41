from .settings import mysettings


__all__ = ['get_context']


def get_context(request=None, site_name=None, title=None, hide_container=None, show_sidenav=None, fixed_sidenav=None,
                primary_color=None, secondary_color=None, primary_color_light=None, primary_color_dark=None,
                success_color=None, error_color=None, link_color=None):
    """Context processor to add nav context to every view.

    Args:
        request (HttpRequest): http request.

        site_name (str)[None]: Name of the site to display in the navbar.
        title (str)[None]: Title to display in the browser tab.

        hide_container (bool)[None]: If True do not use the container and make the contents the full width.
        show_sidenav (bool)[None]: Show the side navigation panel. For larger screens show a menu button to access it.
        fixed_sidenav (bool)[None]: Make the side navigation panel fixed. Setting show_sidenav must be True for this.

        primary_color (str)[None]: String name or hex color to change the primary color.
        secondary_color (str)[None]: String name or hex color to change the secondary color.
        primary_color_light (str)[None]: String name or hex color to change the primary light color.
            This is calculated by default from the primary color.
        primary_color_dark (str)[None]: String name or hex color to change the primary dark color.
            This is calculated by default from the primary color.
        success_color (str)[None]: String name or hex color to change the success color.
        error_color (str)[None]: String name or hex color to change the error color.
        link_color (str)[None]: String name or hex color to change the link color.
    """
    if site_name is None:
        site_name = mysettings.MATERIALIZE_SITE_NAME
    if title is None:
        title = mysettings.MATERIALIZE_TITLE

    if hide_container is None:
        hide_container = mysettings.MATERIALIZE_HIDE_CONTAINER
    if show_sidenav is None:
        show_sidenav = mysettings.MATERIALIZE_SHOW_SIDENAV
    if fixed_sidenav is None:
        fixed_sidenav = mysettings.MATERIALIZE_FIXED_SIDENAV

    if primary_color is None:
        primary_color = mysettings.MATERIALIZE_PRIMARY_COLOR
    if secondary_color is None:
        secondary_color = mysettings.MATERIALIZE_SECONDARY_COLOR
    if primary_color_light is None:
        primary_color_light = mysettings.MATERIALIZE_PRIMARY_COLOR_LIGHT
    if primary_color_dark is None:
        primary_color_dark = mysettings.MATERIALIZE_PRIMARY_COLOR_DARK
    if success_color is None:
        success_color = mysettings.MATERIALIZE_SUCCESS_COLOR
    if error_color is None:
        error_color = mysettings.MATERIALIZE_ERROR_COLOR
    if link_color is None:
        link_color = mysettings.MATERIALIZE_LINK_COLOR

    return {
        'site_name': site_name,
        'title': title,

        'HIDE_CONTAINER': hide_container,
        'SHOW_SIDENAV': show_sidenav,
        'FIXED_SIDENAV': fixed_sidenav,
        'PRIMARY_COLOR': primary_color,
        'SECONDARY_COLOR': secondary_color,
        'PRIMARY_COLOR_LIGHT': primary_color_light,
        'PRIMARY_COLOR_DARK': primary_color_dark,
        'SUCCESS_COLOR': success_color,
        'ERROR_COLOR': error_color,
        'LINK_COLOR': link_color,
        }
