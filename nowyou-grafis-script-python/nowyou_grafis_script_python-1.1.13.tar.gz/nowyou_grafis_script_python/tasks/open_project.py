from ..ui_tools.UI_tools import Ui_tools
from ..utils.utils import resource_path


class OpenProject:

    @staticmethod
    def run():
        OpenProject.open_data()
        OpenProject.open_file()
        OpenProject.select_path()
        OpenProject.input_file()

    # 2a
    @staticmethod
    def open_data():
        Ui_tools.click_on('\static\2a.png')

    # 2b
    @staticmethod
    def open_file():
        Ui_tools.click_on('\static\2b.png')

    # 2c
    @staticmethod
    def select_path():
        # 2ci
        Ui_tools.click_on('\static\2ci.png')
        # 2cii
        Ui_tools.click_on('\static\2cii.png')
        # 2ciii
        Ui_tools.click_on('\static\2ciii.png')
        # 2civ
        Ui_tools.click_on('\static\2civ.png')
        # 2cv
        Ui_tools.click_on('\static\2cv.png')
        # 2cvi
        Ui_tools.click_on('\static\2cvi.png')
        # 2cvii
        Ui_tools.click_on('\static\2cvii.png')

        # 2cviii
        position = Ui_tools.getPosition(resource_path('\static\2cviii.png'))
        if position is not None:
            Ui_tools.click(position)
            Ui_tools.hot_key('ctrl', 'a')
            Ui_tools.hot_key('delete')

    # 2d
    @staticmethod
    def input_file():
        Ui_tools.type("filename")
