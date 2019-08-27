from .mLab_DopplerRadarTool import MainWindow

if __name__ == "__main__":
    print("system start")
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())