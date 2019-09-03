import base64
import io
import logging
import os

from bs4 import BeautifulSoup
from psd_tools import PSDImage
from psd_tools.api.layers import TypeLayer

from psd2html.rw import Reader, Writer

from .logger import logger
from .utils import class_name, style_attrs


def psd2html(psd_path, html_path):
    psd = Reader().load(psd_path)
    if psd:
        writer = Writer(html_path)
        converter = PSD2HTML(psd, writer.save_img)
        if writer.save_html(converter.html_str):
            logging.info('COMPLETED!')

    else:
        logging.info('Terminating...')


class PSD2HTML:
    def __init__(self, psd, save_img=None):
        if hasattr(psd, 'read'):
            psd = PSDImage.open(psd)
        boilerplate = os.path.abspath(os.path.join(os.path.dirname(__file__)) + '/html.txt')
        with open(boilerplate) as fp:
            soup = BeautifulSoup(fp, 'lxml')
        self.soup = soup
        self.save_img = save_img
        content = self._convert(psd)
        self.soup.body.append(content)

    @property
    def html(self):
        return self.soup

    @property
    def html_str(self):
        return self.soup.prettify(formatter="html")

    def _convert(self, layer):
        if isinstance(layer, PSDImage) and not layer and layer.has_preview():
            div = self._convert_img(layer)
        elif layer.is_group():
            div = self._convert_group(layer)
        elif isinstance(layer, TypeLayer):
            div = self._convert_type(layer)
        elif layer.has_pixels():
            div = self._convert_img(layer)
        else:
            div = ''

        return div

    def _convert_img(self, layer):
        img = self.soup.new_tag('img')
        img['style'] = style_attrs(layer)
        img['src'] = self._get_img_src(layer.topil())

        return img

    def _convert_type(self, layer):
        div = self.soup.new_tag('div')
        div['style'] = style_attrs(layer)
        div['class'] = class_name(layer)
        div.append(layer.text)

        return div

    def _convert_group(self, group):
        div = self.soup.new_tag('div')
        div['style'] = style_attrs(group)
        div['class'] = class_name(group)
        for layer in group:
            div.append(self._convert(layer))

        return div

    def _get_img_src(self, image, fmt='png', icc_profile=None):
        with io.BytesIO() as output:
            image.save(output, format=fmt, icc_profile=icc_profile)
            encoded_image = output.getvalue()
        if self.save_img:
            src = self.save_img(encoded_image)
        else:
            src = ('data:image/{};base64,'.format(fmt) + base64.b64encode(encoded_image).decode('utf-8'))

        return src
