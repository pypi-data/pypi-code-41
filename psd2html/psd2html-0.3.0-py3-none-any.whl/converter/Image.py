from psd2html.builder import Img

from .utils import get_attrs


class ImageConvert:
    def convert_img(self, layer):
        attrs = get_attrs(layer)
        src = self._save_img(layer.topil())
        img = Img()
        img.render(src, attrs)
        return img.get()
