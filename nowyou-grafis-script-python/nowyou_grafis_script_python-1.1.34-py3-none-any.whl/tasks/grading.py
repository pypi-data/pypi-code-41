from ..ui_tools.UI_tools import Ui_tools
from ..utils.utils import resource_path

class Grading:

    @staticmethod
    def run():
        Grading.create_size()
        Grading.grade()

    # 3a
    @staticmethod
    def create_size():
        Ui_tools.click_on('\static\\3ai.png')
        Ui_tools.click_on('\static\\3aii.png')
        Ui_tools.click_on('\static\\3aiii.png')
        Ui_tools.click_on('\static\\3aiv.png')
        Ui_tools.click_on('\static\\3av.png')

        # TODO make as input parameter
        Ui_tools.type('Test-name')

        Ui_tools.hot_key('enter')

        Ui_tools.click_on('\static\\3aviii.png')

        position = Ui_tools.getPosition(resource_path('\static\\3aix.png'))
        Ui_tools.click((230 + position[0], position[1]))

        # TODO make as input parameter
        Ui_tools.type('610')

        Ui_tools.hot_key('esc')
        Ui_tools.hot_key('ctrl', 's')
        Ui_tools.hot_key('enter')
        Ui_tools.click_on('\static\\3axii.png')
        Ui_tools.hot_key('esc')
        Ui_tools.hot_key('esc')


    # 3b
    @staticmethod
    def grade():
        Ui_tools.hot_key('ctrl', 'g')
        Ui_tools.click_on('\static\\3bii.png')
        Ui_tools.click_on('\static\\3biii.png')

        position = Ui_tools.getPosition(resource_path('\static\\3biv.png'))
        Ui_tools.click(position)
        Ui_tools.click((60 + position[0], position[1]))

        # TODO make as input parameter
        Ui_tools.type('Test-name')

        Ui_tools.hot_key('enter')
        Ui_tools.hot_key('ctrl', '6')

