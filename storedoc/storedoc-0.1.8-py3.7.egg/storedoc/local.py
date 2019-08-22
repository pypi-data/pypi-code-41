import os

class LocalStorage(object):

    def _get_filename(self, file):
        *_, filename =  file.filename.split('/')
        return filename


    def save_file(self, file, folder=''):
        filename = self._get_filename(file)
        media_location = os.path.join(os.getcwd(), filename)
        if folder and not os.path.exists(folder):
            os.mkdir(folder)
        if folder:
            media_location = os.path.join(os.path.abspath(
                os.path.join(os.getcwd(), folder)
            ), filename)
        file.save(media_location)
        return media_location
