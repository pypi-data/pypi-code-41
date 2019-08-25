from ..ui_tools.UI_tools import Ui_tools


class OpenProject:

    @staticmethod
    def run():
        OpenProject.open_data()
        OpenProject.open_file()
        OpenProject.select_path()
        OpenProject.input_file()
        OpenProject.confirm()
        OpenProject.close_dialog()

    # 2a
    @staticmethod
    def open_data():
        Ui_tools.click_on('\static\\2a.png')

    # 2b
    @staticmethod
    def open_file():
        Ui_tools.hot_key('ctrl', 'shift', 'o')

    # 2c
    @staticmethod
    def select_path():
        Ui_tools.hot_key('delete')

    # 2d
    @staticmethod
    def input_file():
        Ui_tools.type("nowyou-test-grafis")

    @staticmethod
    def confirm():
        Ui_tools.hot_key('enter')

    @staticmethod
    def close_dialog():
        Ui_tools.hot_key('enter')
