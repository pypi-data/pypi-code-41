# Code-sign the generated executable
import os
import subprocess


def sign():
    os.chdir("./dist")

    for binary in ['lifx_control_panel.exe', 'lifx_control_panel-demo.exe', 'lifx_control_panel-debug.exe']:
        subprocess.call([
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.17763.0\x86\signtool.exe",
            "sign", "/debug",
            "/F", "cert.pfx",
            binary,
        ])


if __name__ == "__main__":
    sign()
