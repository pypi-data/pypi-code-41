from psd_tools import PSDImage
from psd_tools.api.layers import TypeLayer


def css_str(styles):
    css = ''
    for style, value in styles.items():
        if type(value) == int:
            css += style + ': ' + str(value) + 'px; '
        else:
            css += style + ': ' + str(value) + '; '
    return css


def class_name(layer):
    return layer.kind + ' ' + layer.name.replace(' ', '_').lower()


def font_styles(layer):
    style_data = layer.engine_dict['StyleRun']['RunArray'][0]['StyleSheet']['StyleSheetData']
    fill = style_data.get('FillColor')['Values']
    styles = {
        'color': 'rgb(' + str(int(255 * fill[1])) + ',' + str(int(255 * fill[2])) + ',' + str(int(255 * fill[3])) + ')'
    }
    size = style_data.get('FontSize')
    if size:
        styles['font-size'] = int(size)

    return styles


def style_attrs(layer):
    if isinstance(layer, PSDImage):
        left = 0
        top = 0
    else:
        left = layer.left - layer.parent.left if layer.parent else layer.left
        top = layer.top - layer.parent.top if layer.parent else layer.top

    style = {
        'left': left,
        'top': top,
        'width': layer.width,
        'height': layer.height,
        'position': 'absolute' if layer.parent else 'relative'
    }
    if hasattr(layer, 'opacity'):
        opacity = layer.opacity / 255.0
        if opacity < 1:
            style['opacity'] = opacity
    if not layer.visible:
        style['visibility'] = 'hidden'
    if isinstance(layer, TypeLayer):
        font_style = font_styles(layer)
        style.update(font_style)

    return css_str(style)
