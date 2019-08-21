from django.utils.html import format_html_join
from django.conf import settings
from wagtail.core import hooks


@hooks.register('insert_editor_js')
def editor_js():
    """Insert slof_from_name javascript in admin javascript"""
    js_files = [
        'wagtailperson/js/slug_from_person_name.js',
    ]
    js_includes = format_html_join(
        '\n',
        '<script src="{0}{1}"></script>',
        (
            (settings.STATIC_URL, filename)
            for filename
            in js_files
        ),
    )
    return js_includes
