def get_attrs(layer):
    attrs = {
        'class': layer.kind + ' ' + layer.name.replace(' ', '_').lower(),
    }
    style = {
        'left': layer.left,
        'right': layer.right,
        'top': layer.top,
        'bottom': layer.bottom,
        'width': layer.width,
        'height': layer.height,
        'visibility': '' if layer.visible else 'hidden',
        'position': 'relative'
    }
    if hasattr(layer, 'opacity'):
        opacity = layer.opacity / 255.0
        if opacity != 0:
            style['opacity'] = opacity
    parent = layer.parent
    if parent:
        style['left'] = layer.left - parent.left
        style['right'] = layer.right - parent.right
        style['top'] = layer.top - parent.top
        style['bottom'] = layer.bottom - parent.bottom
        style['position'] = 'absolute'
    attrs['style'] = style

    return attrs
