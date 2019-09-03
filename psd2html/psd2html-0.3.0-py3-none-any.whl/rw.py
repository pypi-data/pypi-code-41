import hashlib
import os

from psd_tools import PSDImage

from psd2html.storage import get_storage

from .logger import logger

RESOURCE_PATH = 'files/'


class Reader:
    @staticmethod
    def load(path):
        storage = get_storage(os.path.dirname(path))
        filename = os.path.basename(path)
        try:
            with storage.open(filename) as f:
                psd = PSDImage.open(f)
                return psd

        except AttributeError:
            logger.error('Invalid file')
            return False
        except FileNotFoundError:
            logger.error('File not found')
            return False


class Writer:

    def __init__(self, output_data):
        self._resource = get_storage(os.path.join(os.path.dirname(output_data), RESOURCE_PATH), type='res')
        self._output = None
        self._output_file = None
        self._set_output(output_data)

    def _set_output(self, output_data):
        if hasattr(output_data, 'write'):
            self._output = output_data
            return

        if not output_data.endswith('/') and os.path.isdir(output_data):
            output_data += '/'
        self._output = get_storage(os.path.dirname(output_data))
        self._output_file = os.path.basename(output_data)

    def save_html(self, pretty_string):
        if self._output_file:
            url = self._output.url(self._output_file)
            self._output.put(self._output_file, pretty_string.encode('utf-8'))
            return url
        if self._output:
            self._output.write(str(pretty_string))
            return self._output
        return pretty_string

    def save_img(self, encoded_image, fmt='png'):
        if self._resource is not None:
            checksum = hashlib.md5(encoded_image).hexdigest()
            filename = checksum + '.' + fmt
            self._resource.put(filename, encoded_image)
            return os.path.join(RESOURCE_PATH, filename)
        else:
            return False
