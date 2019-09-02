
class FormHandler(QtWidgets.QMainWindow, form.Ui_MainWindow):
    def wc_to_form(self):
        wc_m = self.wc_m.currentText()

        if wc_m == 'GHz':
            self.wc.setText(str(self.config.wc / self.config.GHz))
        elif wc_m == 'MHz':
            self.wc.setText(str(self.config.wc / self.config.MHz))
        elif wc_m == 'KHz':
            self.wc.setText(str(self.config.wc / self.config.KHz))
        else:
            self.wc.setText(str(self.config.wc))

    def wa_to_form(self):
        wa_m = self.wa_m.currentText()

        if wa_m == 'GHz':
            self.wa.setText(str(self.config.wa / self.config.GHz))
        elif wa_m == 'MHz':
            self.wa.setText(str(self.config.wa / self.config.MHz))
        elif wa_m == 'KHz':
            self.wa.setText(str(self.config.wa / self.config.KHz))
        else:
            self.wa.setText(str(self.config.wa))

    def g_to_form(self):
        g_m = self.g_m.currentText()

        if g_m == 'GHz':
            self.g.setText(str(self.config.g / self.config.GHz))
        elif g_m == 'MHz':
            self.g.setText(str(self.config.g / self.config.MHz))
        elif g_m == 'KHz':
            self.g.setText(str(self.config.g / self.config.KHz))
        else:
            self.g.setText(str(self.config.g))

    def T_to_form(self):
        T_m = self.T_m.currentText()

        if T_m == 'mks':
            self.T.setText(str(round(self.config.T / self.config.mks, 3)))
        elif T_m == 'ns':
            self.T.setText(str(round(self.config.T / self.config.ns, 3)))

    def read_config(self):
        self.config = load_pkg("config", "src/Bipartite/config.py")
        self.capacity.setText(str(self.config.capacity))
        self.n.setText(str(self.config.n))
        self.wc.setText(str(self.config.wc))
        self.wa.setText(str(self.config.wa))
        self.g.setText(str(self.config.g))
        self.T.setText(str(self.config.T))
        self.nt.setText(str(self.config.nt))

    def T_m_change(self):
        self.T_to_form()

    def read_T(self, config):
        T = float(self.T.text())
        print(T)

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.read_config()
        self.run_btn.clicked.connect(self.run)

        self.wc_m.currentIndexChanged.connect(self.wc_to_form)
        self.wa_m.currentIndexChanged.connect(self.wa_to_form)
        self.g_m.currentIndexChanged.connect(self.g_to_form)
        self.T_m.currentIndexChanged.connect(self.T_to_form)

        self.read_T(self.config)

        self.wc_to_form()
        self.wa_to_form()
        self.g_to_form()
        self.T_to_form()

    def run(self):
        capacity = self.capacity.text()
        n = self.n.text()

        wc = self.wc.text()
        wa = self.wa.text()
        g = self.g.text()

        T = self.T.text()
        nt = self.nt.text()

        make_config(capacity, n, wc, wa, g, T, nt)

        run_bp.run()
        # cv = Cavity(n=n, wc=wc, wa=wa, g=g)

        # print(cv)
        # make_config(capacity, n, wc, wa, g)

        # os.system("python3 ../Python/Bipartite.py")
        # print(self.n.text())
