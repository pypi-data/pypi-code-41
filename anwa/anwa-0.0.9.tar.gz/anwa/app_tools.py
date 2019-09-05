# /usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import sys
import os.path as op


def create_icon(app_name:str, conda_env_name=None, icon_filename=None, package_name=None):
    import platform
    # print(platform.system)
    if conda_env_name is None:
        conda_env_name = app_name

    if icon_filename is None:
        icon_filename = app_name

    if Path(icon_filename).suffix == "":
        icon_filename += ".ico"

    if package_name is None:
        package_name = app_name

    if platform.system() == "Windows":

        # logo_fn2 = pathlib.Path(__file__).parent / pathlib.Path("scaffan_icon512.ico")

        logo_fn = op.join(op.dirname(__file__), icon_filename)
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")

        pth = Path.home()
        pth = pth / "Desktop" / Path(f"{app_name}.lnk")
        shortcut = shell.CreateShortcut(str(pth))
        # cmd
        # ln =  "call activate scaffan; {} -m scaffan".format(sys.executable)
        # C:\Windows\System32\cmd.exe /C "call activate anwaapp & pause &  python -m anwa & pause"
        # shortcut.TargetPath = sys.executable
        # shortcut.Arguments = f"-m {app_name}"
        shortcut.TargetPath = "cmd"
        # C:\Windows\System32\cmd.exe /C "call activate anwaapp & pause &  python -m anwa & pause"
        shortcut.Arguments = f'/C "call activate {conda_env_name} & python -m {package_name} & pause" '
        shortcut.IconLocation = "{},0".format(logo_fn)
        shortcut.Save()
