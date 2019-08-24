import utils.utils as utils
import script.ui_tools as ui_tools


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
        ui_tools.Ui_tools.click_on('\static\2a.png')

    # 2b
    @staticmethod
    def open_file():
        ui_tools.Ui_tools.click_on('\static\2b.png')

    # 2c
    @staticmethod
    def select_path():
        # 2ci
        ui_tools.Ui_tools.click_on('\static\2ci.png')
        # 2cii
        ui_tools.Ui_tools.click_on('\static\2cii.png')
        # 2ciii
        ui_tools.Ui_tools.click_on('\static\2ciii.png')
        # 2civ
        ui_tools.Ui_tools.click_on('\static\2civ.png')
        # 2cv
        ui_tools.Ui_tools.click_on('\static\2cv.png')
        # 2cvi
        ui_tools.Ui_tools.click_on('\static\2cvi.png')
        # 2cvii
        ui_tools.Ui_tools.click_on('\static\2cvii.png')

        # 2cviii
        position = ui_tools.Ui_tools.getPosition(utils.resource_path('\static\2cviii.png'))
        if position is not None:
            ui_tools.Ui_tools.click(position)
            ui_tools.Ui_tools.hot_key('ctrl', 'a')
            ui_tools.Ui_tools.hot_key('delete')

    # 2d
    @staticmethod
    def input_file():
        ui_tools.Ui_tools.type("filename")
