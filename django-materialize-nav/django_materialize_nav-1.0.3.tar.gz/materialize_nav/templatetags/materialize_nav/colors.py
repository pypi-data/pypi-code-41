from .base import register
from materialize_nav.colors import COLORS, get_rgb, modify_val, lighten, darken, saturate, desaturate, opacify, \
    transparentize, set_opacity, to_rgb, to_rgba


CACHE = {}


@register.inclusion_tag("materialize_nav/dynamic_css.html", takes_context=True)
def include_dynamic_css(context, primary_color=None, primary_color_light=None, primary_color_dark=None,
                        secondary_color=None, success_color=None, error_color=None, link_color=None):
    """Return the html style tag to change default colors.

    This function saves 'include_custom_color' results in a dictionary and recalls that dictionary for speed.
    """
    primary_color = primary_color or context.get('PRIMARY_COLOR', None)
    primary_color_light = primary_color_light or context.get('PRIMARY_COLOR_LIGHT', None)
    primary_color_dark = primary_color_dark or context.get('PRIMARY_COLOR_DARK', None)
    secondary_color = secondary_color or context.get('SECONDARY_COLOR', None)
    success_color = success_color or context.get('SUCCESS_COLOR', None)
    error_color = error_color or context.get('ERROR_COLOR', None)
    link_color = link_color or context.get('LINK_COLOR', None)

    args = (primary_color, primary_color_light, primary_color_dark,
            secondary_color, success_color, error_color, link_color)
    if all((a is None for a in args)):
        return ''

    try:
        return CACHE[args]
    except KeyError:
        pass

    results = get_custom_color_context(*args)
    CACHE[args] = results
    return results


def get_custom_color_context(primary_color=None, primary_color_light=None, primary_color_dark=None,
                             secondary_color=None, success_color=None, error_color=None, link_color=None):
    """This includes the html style tag to change the default colors.

    In general this should not be called 'include_dynamic_css' should be called.
    """
    change = {}
    if primary_color:
        primary_color = COLORS.get(primary_color, primary_color)
        if primary_color_light is None:
            primary_color_light = lighten(primary_color, 15)
        if primary_color_dark is None:
            primary_color_dark = darken(primary_color, 15)

        # ===== Primary Color =====
        change["primary_color"] = primary_color
        change["primary_color_light"] = primary_color_light
        change["primary_color_dark"] = primary_color_dark
        change["tabs_text_color"] = primary_color
        change['tabs_underline_color'] = primary_color_light
        change["tabs_text_color_active"] = to_rgba(get_rgb(primary_color)[:3] + (0.7,))
        change["tabs_text_color_disabled"] = to_rgba(get_rgb(primary_color)[:3] + (0.4,))
        change["footer_bg_color"] = primary_color

    if secondary_color:
        secondary_color = COLORS.get(secondary_color, secondary_color)
        change["secondary_color"] = secondary_color

        change["badge_bg_color"] = secondary_color

        change["button_background_focus"] = lighten(secondary_color, 4)
        change["button_raised_background"] = secondary_color
        change['button_raised_background_focus'] = darken(change["button_raised_background"], 10)  # Manually created
        change["button_raised_background_hover"] = lighten(change["button_raised_background"], 5)
        change["button_floating_background"] = secondary_color
        change["button_floating_background_hover"] = change["button_floating_background"]

        change["datepicker_weekday_bg"] = darken(secondary_color, 7)
        change["datepicker_date_bg"] = secondary_color
        change["datepicker_selected"] = secondary_color
        change["datepicker_selected_outfocus"] = desaturate(lighten(secondary_color, 35), 15)
        change["datepicker_day_focus"] = transparentize(desaturate(secondary_color, 5), .75)

        change["dropdown_color"] = secondary_color

        change["input_focus_color"] = secondary_color

        change["radio_fill_color"] = secondary_color
        change["radio_border"] = "2px solid " + change["radio_fill_color"]

        change["select_focus"] = "1px solid " + lighten(secondary_color, 47)

        change["switch_bg_color"] = secondary_color
        change["switch_bg_color_transparentize"] = transparentize(change['switch_bg_color'], .85)  # Manually created
        change["switch_checked_lever_bg"] = desaturate(lighten(change["switch_bg_color"], 25), 25)

        change["spinner_default_color"] = secondary_color

        change['timepicker_tick_hover'] = transparentize(secondary_color, .75)  # Manually created

        change["collection_active_bg_color"] = secondary_color
        change["collection_active_color"] = lighten(secondary_color, 55)
        change["collection_link_color"] = secondary_color

        change["progress_bar_color"] = secondary_color
        change["progress_bar_color_lighten"] = lighten(change['progress_bar_color'], 40)  # Manually created

    if success_color:
        success_color = COLORS.get(success_color, success_color)
        change["success_color"] = success_color
        change["input_success_color"] = success_color

    if error_color:
        error_color = COLORS.get(error_color, error_color)
        change["error_color"] = error_color
        change["input_error_color"] = error_color
        change["input_invalid_border"] = "1px solid " + error_color

    if link_color:
        link_color = COLORS.get(link_color, link_color)
        change["link_color"] = link_color

    return change
