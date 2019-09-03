from psd2html.builder import Div

from .utils import get_attrs


class TypeConvert:

    def convert_type(self, layer):
        attrs = self._get_type_attrs(layer)
        div = Div()
        div.render(attrs, layer.text)
        return div.get()

    def _get_color(self, layer):
        style_data = layer.engine_dict['StyleRun']['RunArray'][0]['StyleSheet']['StyleSheetData']
        fill = style_data.get('FillColor')['Values']
        rgb = 'rgb(' + str(int(255 * fill[1])) + ',' + str(int(255 * fill[2])) + ',' + str(int(255 * fill[3])) + ')'
        return rgb

    def _get_type_attrs(self, layer):
        style = {
            'color': self._get_color(layer)
        }
        attrs = get_attrs(layer)
        attrs['style'] = {**attrs['style'], **style}
        return attrs
