
from django import template
from psu_base.classes.Log import Log
from psu_base.services import utility_service, auth_service
import psu_base.templatetags.tag_processing.supporting_functions as support
from psu_base.classes.User import User

log = Log()


class SelectNode(template.Node):
    """Generates a select menu with automated option selection"""
    def __init__(self, args):
        self.args = args

    def render(self, context):
        # Prepare attributes
        attrs = support.process_args(self.args, context)

        # Attributes that need special processing are 'options' and 'value'
        options = value = None

        # Make nullable by default
        nullable = True
        if 'nullable' in attrs:
            nullable = str(attrs.get('nullable')).lower() not in ['n', 'false', 'none']

        # Allow default null label to be overwritten
        null_label = attrs.get('null_label') if 'null_label' in attrs else "Select an Option"

        # Expect options to be provided
        if 'options' in attrs:
            options = attrs.get('options')
        else:
            log.error("You must provide a dict of options for the select menu")
            options = {}

        # Could be multiple-select
        multiple = str(attrs.get('multiple')).lower() in ['multiple', 'true', 'y']
        # Expect a value or values to be provided
        value = attrs.get('value')
        values = attrs.get('values')

        # Remove special attrs that should not appear in the HTML element
        for ii in ['multiple', 'values', 'value', 'null_label', 'nullable', 'options']:
            if ii in attrs:
                del attrs[ii]

        pieces = ["<select"]
        for attr_key, attr_val in attrs.items():
            pieces.append(f"{attr_key}=\"{attr_val}\"")
        if multiple:
            pieces.append("multiple")
        pieces.append(">")
        for option_key, option_val in options.items():
            pieces.append(f"<option value=\"{option_key}\"")
            if value == option_key:
                pieces.append('selected')
            elif multiple and values and option_key in values:
                pieces.append('selected')
            pieces.append(f">{option_val}</option>")
        pieces.append("</select>")

        return ' '.join(pieces)


class FaNode(template.Node):
    """Handles the FontAwesome icon-generating tag"""
    def __init__(self, args):
        self.args = args

    def render(self, context):
        attrs = support.process_args(self.args, context)
        # The FontAwesome (fa) classes are expected to be given first, without key="val" formatting
        # Collect all assumed fa classes first
        fa_classes = {k: v for k, v in attrs.items() if k == v}

        # Everything else should have been in key="value" format
        other_attributes = {k: v for k, v in attrs.items() if k != v}

        # Determine screen reader text
        if other_attributes.get('aria-hidden', 'false').lower() == 'true':
            aria_text = ""
        elif other_attributes.get("aria-label"):
            aria_text = other_attributes.get("aria-label")
            del other_attributes["aria-label"]
        elif other_attributes.get('title'):
            aria_text = other_attributes.get('title')
        else:
            aria_text = ""
        # If screen reader text was found, put it in a sr-only span
        if aria_text:
            aria_text = f"<span class=\"sr-only\">{aria_text}</span>"

        # Icon will be wrapped in a button if it has an onclick action
        onclick = other_attributes.get('onclick')
        classes = other_attributes.get('class')
        if onclick:
            del other_attributes['onclick']
            if classes:
                del other_attributes['class']
            else:
                classes = ""
            icon = [f"<button type=\"button\" onclick=\"{onclick}\" class=\"btn btn-icon {classes}\""]
        else:
            icon = ["<span"]

        for kk, vv in other_attributes.items():
            icon.append(f" {kk}=\"{vv}\"")
        icon.append('>')

        # Build a basic FA icon inside the div or button
        icon.append('<span class="fa')
        for fa_class in fa_classes:
            icon.append(f" {fa_class}")
        icon.append('"')
        # Icon should always be aria-hidden, since title/label was printed in an sr-only span
        icon.append(' aria-hidden="true"')
        icon.append('></span>')

        # Append hidden screen reader text, if present
        icon.append(aria_text)

        # Close the button or span wrapper
        if onclick:
            icon.append("</button>")
        else:
            icon.append("</span>")

        return ' '.join(icon)


class ImageNode(template.Node):
    def __init__(self, args):
        self.args = args

    def render(self, context):
        log.trace(self.args)
        # Prepare attributes
        attrs = {}
        for arg in self.args[1:]:
            key = val = None
            if '=' in arg:
                key, val = arg.split('=')
            else:
                log.warn(
                    f"Ignoring invalid argument for image tag: {arg}. Arguments must be in 'key=\"value\" format"
                )
                continue

            if val.startswith('"'):
                val = val.strip('"')
            else:
                val_str = template.Variable(val)
                val = val_str.resolve(context)

            # Allow src attribute to be called other things in this case
            if key.lower() in ['src', 'source', 'image', 'file', 'path', 'filename']:
                key = 'src'

            attrs[key.lower()] = val

        # Prepend the static content url to the src
        if 'src' in attrs:
            attrs['src'] = f"{utility_service.get_static_content_url()}/images/{attrs['src']}"
        # If no src was given, log warning and use empty src (for broken image indicator)
        else:
            log.warn("No image file name was provided as 'src' in the 'image' taglib")
            attrs['src'] = ""

        pieces = [f"<img"]
        for attr_key, attr_val in attrs.items():
            pieces.append(f"{attr_key}=\"{attr_val}\"")
        pieces.append("/>")

        return ' '.join(pieces)


class PhotoNode(template.Node):
    def __init__(self, args):
        self.args = args

    def render(self, context):
        attrs = support.process_args(self.args, context)

        # A user object must be provided
        user_instance = attrs.get('user')
        if not user_instance:
            log.warn("No user attribute was provided. ID photo cannot be displayed")

        # Does the user have a photo?
        if user_instance and user_instance.id_photo:
            src = user_instance.id_photo
            default_alt = f"ID photo of {user_instance.display_name}"
            has_img = True
        else:
            src = f"{utility_service.get_static_content_url()}/images/no-id-photo.png"
            default_alt = "Missing ID photo"
            has_img = False
            if user_instance and user_instance.display_name:
                default_alt += f" for {user_instance.display_name}"

        # Prepare attributes
        attrs = {}
        nvl = False
        for arg in self.args[1:]:
            key = val = None
            if '=' in arg:
                key, val = arg.split('=')
            elif arg == 'user_instance':
                continue
            else:
                log.warn(
                    f"Ignoring invalid argument for id_photo tag: {arg}. Arguments must be in 'key=\"value\" format"
                )
                continue

            if key.lower() == 'src':
                log.warn("Ignoring src attribute in id_photo tag. The src is determined automatically.")
            elif key.lower() == 'nvl':
                # Any value means True, except false or no
                nvl = val.lower() not in ['false', 'no', 'n']
            else:
                if val.startswith('"'):
                    val = val.strip('"')
                else:
                    val_str = template.Variable(val)
                    val = val_str.resolve(context)

                attrs[key.lower()] = val

        # If alt not provided, use default
        if 'alt' not in attrs:
            attrs['alt'] = default_alt

        # If no classes provided, use default class
        if 'class' not in attrs:
            attrs['class'] = 'id_photo'

        # If a valid user has no image, and using nvl, render their initials instead of a picture
        if user_instance and user_instance.is_valid() and (not has_img) and nvl:
            pieces = [f"<span"]
            for attr_key, attr_val in attrs.items():
                pieces.append(f"{attr_key}=\"{attr_val}\"")
            pieces.append(">")
            pieces.append(f"<div class=\"id_photo-nvl\">{user_instance.first_name[:1]}{user_instance.last_name[:1]}</div>")
            pieces.append("</span>")
        else:
            pieces = [f"<img src=\"{src}\""]
            for attr_key, attr_val in attrs.items():
                pieces.append(f"{attr_key}=\"{attr_val}\"")
            pieces.append("/>")

        return ' '.join(pieces)


def pagination(paginated_results):
    """Example: {%pagination polls%}"""
    # Show three pages on either side of the current page
    current_page = paginated_results.number     # 10    2
    min_page = current_page - 3                 # 7     -1
    max_page = current_page + 3                 # 13    5

    # If starting before page 1, shift min and max to be higher
    while min_page < 1:
        min_page += 1
        max_page += 1

    # If Extending past the last page, shift min and max lower
    while max_page > paginated_results.paginator.num_pages:
        min_page -= 1
        max_page -= 1

    # If shifting resulted in page less than 1, set it to page 1
    if min_page < 1:
        min_page = 1

    # Show dots to indicate pages not displayed?
    dots_before = bool(min_page > 1)
    dots_after = bool(max_page < paginated_results.paginator.num_pages)

    return {
        'paginated_results': paginated_results,
        'min_page': min_page,
        'max_page': max_page,
        'dots_before': dots_before,
        'dots_after': dots_after,
    }
