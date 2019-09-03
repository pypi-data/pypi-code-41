from psd_tools import PSDImage
from psd_tools.api.layers import TypeLayer

from psd2html.builder import Div
from psd2html.converter.Image import ImageConvert
from psd2html.converter.Type import TypeConvert
from psd2html.converter.utils import get_attrs


class LayerConvert(TypeConvert, ImageConvert):

    def convert_layer(self, layer):
        if isinstance(layer, PSDImage) and not layer and layer.has_preview():
            element = self.convert_img(layer)
        elif layer.is_group():
            element = self._convert_group(layer)
        elif isinstance(layer, TypeLayer):
            element = self.convert_type(layer)
        elif layer.has_pixels():
            element = self.convert_img(layer)
        else:
            element = None

        return element

    def _convert_group(self, group, container=None):
        if not container:
            container = Div()
            attrs = get_attrs(group)
            container.render(attrs)
        for layer in group:
            element = self.convert_layer(layer)
            if not element:
                continue
            container.append(element)

        return container.get()
