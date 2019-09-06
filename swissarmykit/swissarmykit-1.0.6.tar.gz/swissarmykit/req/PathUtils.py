try: from definitions_prod import *
except Exception as e: pass

import os
from swissarmykit.utils.fileutils import FileUtils
from swissarmykit.req.RequestBase import RequestBase

class PathUtils(RequestBase):

    def __init__(self):
        super().__init__()

    def get_download_images_path(self, sub_path='', num_folder=False, is_favicon=False):
        if is_favicon:
            return appConfig.get_images_path() + '/' + self.__class__.__name__ + '/favicon'

        sub_path = sub_path.strip().strip('/')
        sub_path = '/' + sub_path if sub_path else ''  # use for download avatar
        return appConfig.get_images_path() + '/' + self.__class__.__name__ + ('/%d' if num_folder else '') + sub_path

    def get_output_path(self):
        return appConfig.HTML_PATH + '/' + str(self.__class__.__name__)

    def get_html_path(self, file_name=None):
        path = appConfig.HTML_PATH + '/' + str(self.__class__.__name__)
        if file_name != None:
            return path + '/' + str(file_name)
        return path

    def html_to_desktop(self, html):
        file_name = appConfig.USER_DESKTOP + '/_' + self.__class__.__name__ + '.html'
        FileUtils.to_html_file(file_name, html)
        print('INFO: html to desktop: %s' % file_name)

    def get_folder_by(self, cat='', sub_cat=''):
        '''
        Get folder by class which invoked.
        :param cat: Category
        :param sub_cat: Subcategory
        :return:
        '''
        if cat and sub_cat:
            sub_cat = FileUtils.get_valid_file_path(cat) + '/' + FileUtils.get_valid_file_path(sub_cat)
        elif cat:
            sub_cat = FileUtils.get_valid_file_path(cat)
        else:
            sub_cat = ''

        file_path = self.get_download_images_path(sub_path=sub_cat, num_folder=False)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        return file_path

    def is_not_exists(self, file_name):
        file_name = str(file_name)
        if '/' in file_name:
            raise Exception('Only file name, no path: %s' % file_name)

        file_path = self.get_html_path(file_name)
        if os.path.exists(file_path) and FileUtils.get_file_size(file_path):
            return False
        return True
