import win32com.shell.shell as shell
import win32event
import utils.utils as utils
import script.ui_tools as ui_tools


class Launch:

    @staticmethod
    def run():
        Launch.launch_grafis()
        Launch.close_new_version_modal()
        Launch.close_temporary_files_modal()

    # 1a
    @staticmethod
    def launch_grafis():
        se_ret = shell.ShellExecuteEx(fMask=0x140, lpFile=r"D:\games\blender.lnk", nShow=1)
        win32event.WaitForSingleObject(se_ret['hProcess'], -1)

    # 1b
    @staticmethod
    def close_new_version_modal():
        ui_tools.Ui_tools.hot_key('Esc')

    # 1c
    @staticmethod
    def close_temporary_files_modal():
        position = ui_tools.Ui_tools.getPosition(utils.resource_path('\static\1b.png'))

        if position is not None:
            ui_tools.Ui_tools.hot_key('Esc')
