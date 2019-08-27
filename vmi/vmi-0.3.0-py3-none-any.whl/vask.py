import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import vmi

desktop = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
policyMin = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
tr = QObject()
tr = tr.tr


def askOpenFile(nameFilter='*', title: str = tr('请选择打开文件 (Please select open file)')):
    s = QSettings()

    d = QFileDialog(None, title, s.value('Last' + title, defaultValue=desktop))
    d.setAcceptMode(QFileDialog.AcceptOpen)
    d.setFileMode(QFileDialog.ExistingFile)
    d.setViewMode(QFileDialog.Detail)
    d.setFilter(QDir.AllEntries | QDir.NoSymLinks | QDir.NoDotAndDotDot)
    d.setNameFilter(nameFilter)

    if d.exec_() != QDialog.Accepted or len(d.selectedFiles()) < 1:
        return None

    s.setValue('Last' + title, d.selectedFiles()[0])
    return d.selectedFiles()[0]


def askSaveFile(suffix='*', nameFilter=None, title: str = tr('请选择保存文件 (Please select save file)')):
    s = QSettings()

    d = QFileDialog(None, title, s.value('Last' + title, defaultValue=desktop))
    d.setAcceptMode(QFileDialog.AcceptSave)
    d.setFileMode(QFileDialog.AnyFile)
    d.setViewMode(QFileDialog.Detail)
    d.setFilter(QDir.AllEntries | QDir.NoSymLinks | QDir.NoDotAndDotDot)
    d.setDefaultSuffix(suffix)
    d.setNameFilter(nameFilter)

    if nameFilter is None:
        d.setNameFilter(suffix)

    if d.exec_() != QDialog.Accepted or len(d.selectedFiles()) < 1:
        return None

    s.setValue('Last' + title, d.selectedFiles()[0])
    return d.selectedFiles()[0]


def askOpenFiles(title: str = tr('请选择打开文件 (Please select open files)')):
    s = QSettings()

    d = QFileDialog(None, title, s.value('Last' + title, defaultValue=desktop))
    d.setAcceptMode(QFileDialog.AcceptOpen)
    d.setFileMode(QFileDialog.ExistingFiles)
    d.setViewMode(QFileDialog.Detail)
    d.setFilter(QDir.AllEntries | QDir.NoSymLinks | QDir.NoDotAndDotDot)

    if d.exec_() != QDialog.Accepted or len(d.selectedFiles()) < 1:
        return None

    s.setValue('Last' + title, QFileInfo(d.selectedFiles()[0]).absolutePath())
    return d.selectedFiles()


def askDirectory(title: str = tr('请选择文件夹 (Please select directory)')):
    s = QSettings()

    d = QFileDialog(None, title, s.value('Last' + title, defaultValue=desktop))
    d.setAcceptMode(QFileDialog.AcceptOpen)
    d.setFileMode(QFileDialog.Directory)
    d.setViewMode(QFileDialog.Detail)
    d.setFilter(QDir.AllEntries | QDir.NoSymLinks | QDir.NoDotAndDotDot)

    if d.exec_() != QDialog.Accepted or len(d.selectedFiles()) < 1:
        return None

    s.setValue('Last' + title, d.selectedFiles()[0])
    return d.selectedFiles()[0]


def _dialog(widgets, title):
    dialog = QDialog()
    dialog.setSizePolicy(policyMin)
    dialog.setWindowTitle(title)
    dialog.setLayout(QVBoxLayout())

    button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
    button.setSizePolicy(policyMin)
    button.accepted.connect(dialog.accept)
    button.rejected.connect(dialog.reject)

    for w in widgets:
        w.setParent(dialog)
        dialog.layout().addWidget(w)
    dialog.layout().addWidget(button)
    return dialog


def askSeries(series, title: str = tr('请选择目标系列 (Please select the target series)')):
    items = [str(i) for i in series]

    def tabCloseRequested(i):
        del items[i]
        tabs.removeTab(i)

    tabs = QTabWidget()
    tabs.setTabsClosable(True)
    tabs.setSizePolicy(policyMin)
    tabs.tabCloseRequested.connect(tabCloseRequested)

    for i in items:
        label = QLabel(text=i)
        tabs.addTab(label, str(tabs.count() + 1))

    d = _dialog([tabs], title)
    if d.exec_() == QDialog.Accepted:
        if 0 <= tabs.currentIndex() < len(series):
            return series[tabs.currentIndex()]
    return None


def askInt(valueMin, value, valueMax, prefix=None, suffix=None, step=None, title: str = tr('输入数值 (Input value)')):
    w = QGroupBox(prefix)
    w.setSizePolicy(policyMin)
    w.setLayout(QHBoxLayout())

    spinbox = QSpinBox(w)
    spinbox.setSizePolicy(policyMin)
    spinbox.setAlignment(Qt.AlignCenter)
    spinbox.setRange(valueMin, valueMax)
    spinbox.setValue(value)
    w.layout().addWidget(spinbox)

    if suffix is not None:
        spinbox.setSuffix(' ' + suffix)

    if step is not None:
        spinbox.setSingleStep(step)
        spinbox.setStepType(QSpinBox.DefaultStepType)
    else:
        spinbox.setStepType(QSpinBox.AdaptiveDecimalStepType)

    d = _dialog([w], title)
    if d.exec_() == QDialog.Accepted:
        return spinbox.value()
    return None


def askInts(valueMin, value, valueMax, prefix=None, suffix=None, step=None,
            title=tr('输入数值 (Input value)')):
    w = QGroupBox(prefix)
    w.setSizePolicy(policyMin)
    w.setLayout(QHBoxLayout())

    spinbox = []
    for i in range(len(value)):
        spinbox.append(QSpinBox(w))
        spinbox[-1].setSizePolicy(policyMin)
        spinbox[-1].setAlignment(Qt.AlignCenter)
        spinbox[-1].setRange(valueMin[i], valueMax[i])
        spinbox[-1].setValue(value[i])
        w.layout().addWidget(spinbox[-1])

        if suffix is not None:
            spinbox[-1].setSuffix(' ' + suffix[i])

        if step is not None:
            spinbox[-1].setSingleStep(step[i])
            spinbox[-1].setStepType(QSpinBox.DefaultStepType)
        else:
            spinbox[-1].setStepType(QSpinBox.AdaptiveDecimalStepType)

    d = _dialog([w], title)
    if d.exec_() == QDialog.Accepted:
        return [spinbox[i].value() for i in range(len(value))]
    return None


def askFloat(valueMin, value, valueMax, decimals, prefix=None, suffix=None, step=None,
             title: str = tr('输入数值 (Input value)')):
    w = QGroupBox(prefix)
    w.setSizePolicy(policyMin)
    w.setLayout(QHBoxLayout())

    spinbox = QDoubleSpinBox(w)
    spinbox.setSizePolicy(policyMin)
    spinbox.setAlignment(Qt.AlignCenter)
    spinbox.setDecimals(decimals)
    spinbox.setRange(valueMin, valueMax)
    spinbox.setValue(value)
    w.layout().addWidget(spinbox)

    if suffix is not None:
        spinbox.setSuffix(' ' + suffix)

    if step is not None:
        spinbox.setSingleStep(step)
        spinbox.setStepType(QSpinBox.DefaultStepType)
    else:
        spinbox.setStepType(QSpinBox.AdaptiveDecimalStepType)

    d = _dialog([w], title)
    if d.exec_() == QDialog.Accepted:
        return spinbox.value()
    return None


def askFloats(valueMin, value, valueMax, decimals, prefix=None, suffix=None, step=None,
              title=tr('输入数值 (Input value)')):
    w = QGroupBox(prefix)
    w.setSizePolicy(policyMin)
    w.setLayout(QHBoxLayout())

    spinbox = []
    for i in range(len(value)):
        spinbox.append(QDoubleSpinBox(w))
        spinbox[-1].setSizePolicy(policyMin)
        spinbox[-1].setAlignment(Qt.AlignCenter)
        spinbox[-1].setDecimals(decimals)
        spinbox[-1].setRange(valueMin[i], valueMax[i])
        spinbox[-1].setValue(value[i])
        w.layout().addWidget(spinbox[-1])

        if suffix is not None:
            spinbox[-1].setSuffix(' ' + suffix[i])

        if step is not None:
            spinbox[-1].setSingleStep(step[i])
            spinbox[-1].setStepType(QSpinBox.DefaultStepType)
        else:
            spinbox[-1].setStepType(QSpinBox.AdaptiveDecimalStepType)

    d = _dialog([w], title)
    if d.exec_() == QDialog.Accepted:
        return [spinbox[i].value() for i in range(len(value))]
    return None


def askInfo(text: str, title: str = tr('提示 (info)')):
    QMessageBox.information(None, title, text)


def askYesNo(text: str, title: str = tr('是否 (yes or no)')):
    return QMessageBox.question(None, title, text) == QMessageBox.Yes


if __name__ == '__main__':
    vmi.app.setApplicationName('vmi')

    askInt(-3071, -1, 1024, 'CT: [-3071, 1024]', 'HU')
    sys.exit(vmi.app.exec_())
