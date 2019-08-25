from ..ui_tools.UI_tools import Ui_tools
from time import sleep


class Project:

    @staticmethod
    def open_project():
        # 2a
        Ui_tools.hot_key('ctrl', 'shift', 'o')

        # 2c
        Ui_tools.hot_key('delete')

        # 2d
        # TODO make as input parameter
        Ui_tools.type("nowyou-test-grafis")

        Ui_tools.hot_key('enter')
        Ui_tools.hot_key('enter')
        sleep(1)

    @staticmethod
    def save_project():
        Ui_tools.hot_key('ctrl', 's')
        Ui_tools.hot_key('esc')

        # TODO make as input parameter
        Ui_tools.type("nowyou-test-grafis-done")

        Ui_tools.hot_key('enter')
        Ui_tools.hot_key('enter')
        Ui_tools.hot_key('alt', 'f4')

