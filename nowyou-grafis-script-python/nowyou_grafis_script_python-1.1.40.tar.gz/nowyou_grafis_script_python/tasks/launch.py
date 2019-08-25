from ..ui_tools.UI_tools import Ui_tools
from time import sleep

import win32com.shell.shell as shell


class Launch:

    @staticmethod
    def run():
        Launch.launch_grafis()
        Launch.close_new_version_modal()
        Launch.close_temporary_files_modal()

    # 1a
    @staticmethod
    def launch_grafis():
        se_ret = shell.ShellExecuteEx(fMask=0x140, lpFile=r"P:\GRAFIS\Grafis.exe", nShow=1)

    # 1b
    @staticmethod
    def close_new_version_modal():
        sleep(5)

        Ui_tools.click((100, 100))
        Ui_tools.hot_key('Esc')

    # 1c
    @staticmethod
    def close_temporary_files_modal():
        sleep(2)

        Ui_tools.hot_key('Esc')
