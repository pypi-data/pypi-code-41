from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtWinExtras import *
import threading
import time
import os
import sys
import pathlib
import shutil

app = QApplication()
app.setOrganizationName('vmi')
app.setApplicationName('vmi')
app.setStyle(QStyleFactory.create('Fusion'))

appFonts = {}

desktopPath = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
appDataPath = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
os.makedirs(appDataPath, exist_ok=True)

_AppWindow = None
_TaskbarButton = QWinTaskbarButton()
_Progress = _TaskbarButton.progress()

appViews = []


def _appinit():
    fonts = {'alizh': ':/qrc/font/Alibaba-PuHuiTi-Regular.otf',
             'alien': ':/qrc/font/AlibabaSans-Regular.otf'}

    for kw in fonts:
        f = QFile(fonts[kw])
        f.open(QIODevice.ReadOnly)
        bts = f.readAll()
        f.close()

        p = pathlib.Path(appDataPath) / kw
        p.write_bytes(bts)
        appFonts[kw] = str(p)


_appinit()


def appexit():
    for v in appViews:
        v.delete()
    shutil.rmtree(appDataPath, ignore_errors=True)
    sys.exit()


def appwindow(w=None):
    if w is not None:
        global _AppWindow
        _AppWindow = w
        _TaskbarButton.setParent(w)
        _TaskbarButton.setWindow(w.windowHandle())
        _Progress.setVisible(True)
        _Progress.setRange(0, 100)
        _Progress.setValue(0)
    w.show()
    return _AppWindow


def appexec(w):
    appwindow(w)
    app.exec_()


def appwait(thread: threading.Thread, progress=None):
    while thread.isAlive():
        if progress is None:
            value = (_Progress.value() + 5) % 100
        else:
            value = progress[0]
        _Progress.setValue(value)
        time.sleep(0.1)
    _Progress.setValue(0)


scripts = pathlib.Path(sys.executable).parent / 'Scripts'
lupdate = str(scripts / 'pyside2-lupdate')
uic = str(scripts / 'pyside2-uic')
rcc = str(scripts / 'pyside2-rcc')

pyside2 = pathlib.Path(sys.executable).parent / 'Lib/site-packages/PySide2'
designer = str(pyside2 / 'designer')
linguist = str(pyside2 / 'linguist')
lrelease = str(pyside2 / 'lrelease')


def uic_exec(ui_dir: str = 'ui', py_dir: str = '.', prefix: str = 'Ui_'):
    """将ui_dir目录下的所有.ui文件转换到py_dir目录下并附加前缀ui_"""
    py_dir = pathlib.Path(py_dir)

    for ui in pathlib.Path(ui_dir).rglob('*.ui'):
        if ui.is_file():
            py = py_dir / (prefix + ui.with_suffix('.py').name)
            os.system(uic + ' ' + str(ui) + ' -o ' + str(py) + ' -x')
            print('[uic.exe]', uic, ui, '-o', py, '-x')


def lupdate_exec(py_dir: str = '.', ts: str = 'zh_CN.ts'):
    """将py_dir目录下的所有.py文件更新翻译到同目录下的.ts文件o_name"""
    py_dir = pathlib.Path(py_dir)
    pys = str()

    for py in pathlib.Path(py_dir).rglob('*.py'):
        if py.is_file():
            pys += str(py) + ' '

    if len(pys) > 0:
        ts = py_dir / ts
        os.system(lupdate + ' ' + str(pys) + ' -ts ' + str(ts))
        print('[lupdate.exe]', lupdate, pys, '-ts', ts)


def lrelease_exec(ts: str = './zh_CN.ts',
                  qm: str = 'qrc/tr/zh_CN.qm'):
    """将可读ts翻译文件转换为二进制qm翻译文件"""
    os.system(lrelease + ' ' + ts + ' -qm ' + qm)
    print('[lrelease.exe]', lrelease, ts, '-qm', qm)
    os.system(linguist + ' ' + './zh_CN.ts')


def rcc_exec(rc_dir: str = 'qrc', qrc: str = 'vmi.qrc', py: str = 'vrc.py'):
    """将rc_dir目录下的所有文件转换为qrc资源文件"""
    rc_dir = pathlib.Path(rc_dir)
    indent = ' ' * 4
    rcs = str()

    for rc in pathlib.Path(rc_dir).rglob('*'):
        if rc.is_file():
            rc = str(rc).replace('\\', '/')
            rcs += indent * 2 + '<file>' + rc + '</file>' + '\n'

    if len(rcs) > 0:
        t = '<!DOCTYPE RCC>'
        t += '<RCC version="1.0">' + '\n'
        t += indent + '<qresource prefix="/">' + '\n'
        t += rcs
        t += indent + '</qresource>' + '\n'
        t += '</RCC>'

        with open(qrc, 'w') as f:
            f.write(t)

        os.system(rcc + ' ' + qrc + ' -o ' + py)
        print('[rcc.exe]', rcc, qrc, '-o', py)


if __name__ == '__main__':
    # uic_exec()  # 更新界面.ui文件
    # lupdate_exec()  # 更新翻译.ts文件
    # lrelease_exec()  # 更新翻译.qm文件
    rcc_exec()  # 更新.qrc文件

    # os.startfile(designer)  # 打开界面.ui文件
