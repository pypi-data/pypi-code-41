#-------------------------------------------------------------------------------
# Name:        PIDCtrlModelWindow
# Purpose:
#
# Author:      elbar
#
# Created:     09/11/2012
# Copyright:   (c) elbar 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from PyQt5 import QtGui, QtCore, QtWidgets
import sys, os
import logging

from Ui_pid_tune_methods_main_window import Ui_MainWindow

import Utils
import PIDRecipe
import PlotWidget as plt
import control
import control_utils

from PIDTuneMethodsAbout import PIDTuneMethodsAboutWindow

#-------------------------------------------------------------------------------
class PIDTuneMethodsWindow(QtWidgets.QMainWindow):
    """ Class wrapper for about window ui """

    def __init__(self):
        super(PIDTuneMethodsWindow,self).__init__()
        # init
        # process params
        self.gain = 0.0
        self.tau = 0.0
        self.dead_time = 0.0
        # PID params
        self.lambda_tau = 0.0
        self.lambda_tau_ratio = 0.0
        self.kc = 0.0
        self.ti = 0.0
        self.td = 0.0
        # window and logger
        self._logger = logging.getLogger('PIDTuneMethodsLog')
        self.setupUI()
        # init transfer functions
        self._proc_tf = None
        self._pid_tf = None
        self._cl_tf = None
        #init plot widgets
        self._proc_step_plot = plt.PlotWidget('Process Step Plot', x_axis='lin', x_label='t [sec]', y_label='mag')
        self._cl_step_plot = plt.PlotWidget('Closed Loop Step Plot', x_axis='lin', x_label='t [sec]', y_label='mag')

    def setupUI(self):
        # create window from ui
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        # setup dialogs
        self._about_dlg = PIDTuneMethodsAboutWindow()
        # init status bar
        self._status_text = QtWidgets.QLabel(self.ui.centralwidget)
        self.ui.statusbar.addWidget(self._status_text, 14)
        self._refresh_status_bar(True)
        # setup toolbar
        self.ui.mainToolBar.addAction(self.ui.actionRefresh)
        self.ui.mainToolBar.addSeparator()
        self.ui.mainToolBar.addAction(self.ui.action_P_Step_Impulse_Response)
        self.ui.mainToolBar.addSeparator()
        self.ui.mainToolBar.addAction(self.ui.action_CL_Step_Impulse_Response)
        self.ui.mainToolBar.addSeparator()
        self.ui.mainToolBar.addAction(self.ui.actionHelp)
        self.ui.mainToolBar.addAction(self.ui.actionAbout)
        self.ui.mainToolBar.addAction(self.ui.actionExit)
        # init window objects
        self.ui.lblLambdaTauRatio.setEnabled(False)
        self.ui.leLambdaTauRatio.setEnabled(False)
        self.ui.lblLambda.setEnabled(False)
        self.ui.leLambda.setEnabled(False)
        # signals-slots
        self.ui.actionRefresh.triggered.connect(self._refresh)
        self.ui.action_P_Step_Impulse_Response.triggered.connect(self._proc_step_imp_resp)
        self.ui.action_CL_Step_Impulse_Response.triggered.connect(self._cl_step_imp_resp)
        self.ui.actionHelp.triggered.connect(self._open_help_file)
        self.ui.actionAbout.triggered.connect(self._about_dlg.show)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.cmbProccess.currentIndexChanged.connect(self._populate_methods_list)
        self.ui.cmbTuneMethod.currentIndexChanged.connect(self._refresh_UI)
        self.ui.cmbPIDType.currentIndexChanged.connect(self._refresh_PID_fields)
        self.ui.sbPade.valueChanged.connect(self._params_changed)
        self.ui.leGain.textChanged.connect(self._params_changed)
        self.ui.leTc.textChanged.connect(self._params_changed)
        self.ui.leDeadTime.textChanged.connect(self._params_changed)
        self.ui.leKc.textChanged.connect(self._params_changed)
        self.ui.leTi.textChanged.connect(self._params_changed)
        self.ui.leTd.textChanged.connect(self._params_changed)
        self.ui.leLambda.textChanged.connect(self._params_changed)
        self.ui.leLambdaTauRatio.textChanged.connect(self._params_changed)
        self.ui.cmbAlgorithm.currentIndexChanged.connect(self._params_changed)
        self.ui.dsba.valueChanged.connect(self._params_changed)
        # populate lists
        self._populate_proccess_list()
        self._populate_methods_list()
        self.ui.cmbAlgorithm.addItem("Ideal")
        self.ui.cmbAlgorithm.addItem("Serial")
        # show window
        self.show()

    def _refresh(self):
        ''' check inputs '''
        _gain_ok = True; _tau_ok = True; _dead_time_ok = True; _lambda_ok = True
        self.gain, _gain_ok = Utils.check_input(self.ui.leGain.text(), "Invalid Gain")
        # First order with dead time
        _sel_first_order = self.ui.cmbProccess.currentText() == "First order"
        if (_sel_first_order):
            self.tau, _tau_ok = Utils.check_input(self.ui.leTc.text(), "Invalid Tc")
        # Lambda or IMC
        _sel_lambda = (self.ui.cmbTuneMethod.currentText() == "Lambda" or
            self.ui.cmbTuneMethod.currentText() == "IMC")
        _method_str = self.ui.cmbTuneMethod.currentText()
        if (_sel_lambda):
            self.dead_time, _dead_time_ok = Utils.check_input(self.ui.leDeadTime.text(), "Invalid Dead Time", False)
            self.lambda_tau, _lambda_ok = Utils.check_input(self.ui.leLambda.text(), "Invalid Closed Loop Time")
        else:
            self.dead_time, _dead_time_ok = Utils.check_input(self.ui.leDeadTime.text(), "Invalid Dead Time", (_method_str != 'Manual'))
        # Integrating
        _sel_integr = (self.ui.cmbProccess.currentText() == "Integrating")
        if (_sel_integr):
            self.dead_time, _dead_time_ok = Utils.check_input(self.ui.leDeadTime.text(), "Invalid Dead Time", False)
        # Everything is OK ?
        _chk_ok = _gain_ok and _tau_ok and _dead_time_ok and _lambda_ok
        if (_chk_ok):
            self._set_PID_params()
            if (_sel_first_order): # first order
                # build transfer functions
                self._proc_tf = control_utils.build_fodt_process_tf(self.gain, self.tau, self.dead_time, self.ui.sbPade.value())
                self._logger.info("FODT Proc : %s" % (self._proc_tf))
                self._pid_tf = control_utils.PID_ALGORITHS[self.ui.cmbAlgorithm.currentIndex()](self.kc, self.ti, self.td, self.ui.dsba.value())
                self._logger.info("PID : %s" % (self._pid_tf ))
                self._refresh_status_bar(False)
            elif (_sel_integr): # integrating
                # build transfer functions
                self._proc_tf = self._proc_tf = control_utils.build_fodt_process_tf(self.gain, self.dead_time, self.ui.sbPade.value())
                self._logger.info("Integr Proc : %s" % (self._proc_tf))
                self._pid_tf = control_utils.PID_ALGORITHS[self.ui.cmbAlgorithm.currentIndex()](self.kc, self.ti, self.td, self.ui.dsba.value())
                self._logger.info("PID : %s" % (self._pid_tf))
                self._refresh_status_bar(False)
            # refresh plots
            if (self._proc_step_plot.plot_dlg.isVisible()):
                self._proc_step_imp_resp()
            if (self._cl_step_plot.plot_dlg.isVisible()):
                self._cl_step_imp_resp()

    def _populate_proccess_list(self):
        ''' populate methods list '''
       # populate proccess combo box
        self.ui.cmbProccess.clear()
        for i in PIDRecipe.PROCCESS:
            self.ui.cmbProccess.addItem(i)

    def _populate_methods_list(self):
        ''' populate methods list '''
       # populate methods combo box
        self.ui.cmbTuneMethod.clear()
        if (self.ui.cmbProccess.currentText() == "First order"):
            for i in PIDRecipe.PID_METHODS_FODT:
                self.ui.cmbTuneMethod.addItem(i)
                self.ui.leTc.setEnabled(True)
                self.ui.leTc.setVisible(True)
                self.ui.lblTc.setEnabled(True)
                self.ui.lblTc.setVisible(True)
        elif (self.ui.cmbProccess.currentText() == "Integrating"):
            for i in PIDRecipe.PID_METHODS_I:
                self.ui.cmbTuneMethod.addItem(i)
                self.ui.leTc.setEnabled(False)
                self.ui.leTc.setVisible(False)
                self.ui.lblTc.setEnabled(False)
                self.ui.lblTc.setVisible(False)
        self.ui.cmbTuneMethod.setCurrentIndex(1)

    def _refresh_UI(self, idx):
        ''' refresh UI '''
        self._populate_PID_type_list(idx)
        if (self.ui.cmbTuneMethod.currentText() == "Lambda" or
           self.ui.cmbTuneMethod.currentText() == "IMC" ):
            self.ui.leKc.setReadOnly(True)
            self.ui.leTi.setReadOnly(True)
            self.ui.leTd.setReadOnly(True)
            self._refresh_imc_lambda_fields(True)
        elif (self.ui.cmbTuneMethod.currentText() == "Manual" ):
            self.ui.leKc.setReadOnly(False)
            self.ui.leTi.setReadOnly(False)
            self.ui.leTd.setReadOnly(False)
            self._refresh_imc_lambda_fields(False)
        else:
            self.ui.leKc.setReadOnly(True)
            self.ui.leTi.setReadOnly(True)
            self.ui.leTd.setReadOnly(True)
            self._refresh_imc_lambda_fields(False)
        self._refresh_status_bar(True)

    def _populate_PID_type_list(self, idx):
        ''' populate PID type lists '''
        # populate PID Types combo box
        self.ui.cmbPIDType.clear()
        if (self.ui.cmbProccess.currentText() == "First order"):
            for i in PIDRecipe.PID_METHODS_TYPES_FODT[idx]:
                self.ui.cmbPIDType.addItem(PIDRecipe.PID_TYPES[i])
        elif (self.ui.cmbProccess.currentText() == "Integrating"):
            for i in PIDRecipe.PID_METHODS_TYPES_I[idx]:
                self.ui.cmbPIDType.addItem(PIDRecipe.PID_TYPES[i])

    def _refresh_imc_lambda_fields(self, en):
        ''' enable-disable lambda fields '''
        self.ui.lblLambda.setEnabled(en)
        self.ui.lblLambda.setVisible(en)
        self.ui.leLambda.setEnabled(en)
        self.ui.leLambda.setVisible(en)        
        self.ui.lblLambdaTauRatio.setEnabled(en)
        self.ui.lblLambdaTauRatio.setVisible(en)         
        self.ui.leLambdaTauRatio.setEnabled(en)
        self.ui.leLambdaTauRatio.setVisible(en)           

    def _refresh_PID_fields(self, idx):
        ''' refresh PID fields '''
        if (self.ui.cmbPIDType.currentText() == "P"):
            self.ui.lblKc.setEnabled(True)
            self.ui.lblKc.setVisible(True)
            self.ui.lblTi.setEnabled(False)
            self.ui.lblTi.setVisible(False)
            self.ui.lblTd.setEnabled(False)
            self.ui.lblTd.setVisible(False)
            self.ui.lbla.setVisible(False)
            self.ui.leKc.setEnabled(True)
            self.ui.leKc.setVisible(True)
            self.ui.leTi.setEnabled(False)
            self.ui.leTi.setVisible(False)
            self.ui.leTd.setEnabled(False)
            self.ui.leTd.setVisible(False)
            self.ui.dsba.setVisible(False)
        elif (self.ui.cmbPIDType.currentText() == "PI"):
            self.ui.lblKc.setEnabled(True)
            self.ui.lblKc.setVisible(True)
            self.ui.lblTi.setEnabled(True)
            self.ui.lblTi.setVisible(True)
            self.ui.lblTd.setEnabled(False)
            self.ui.lblTd.setVisible(False)
            self.ui.lbla.setVisible(False)
            self.ui.leKc.setEnabled(True)
            self.ui.leKc.setVisible(True)
            self.ui.leTi.setEnabled(True)
            self.ui.leTi.setVisible(True)
            self.ui.leTd.setEnabled(False)
            self.ui.leTd.setVisible(False)
            self.ui.dsba.setVisible(False)
        elif (self.ui.cmbPIDType.currentText() == "PID"):
            self.ui.lblKc.setEnabled(True)
            self.ui.lblKc.setVisible(True)
            self.ui.lblTi.setEnabled(True)
            self.ui.lblTi.setVisible(True)
            self.ui.lblTd.setEnabled(True)
            self.ui.lblTd.setVisible(True)
            self.ui.lbla.setVisible(True)
            self.ui.leKc.setEnabled(True)
            self.ui.leKc.setVisible(True)
            self.ui.leTi.setEnabled(True)
            self.ui.leTi.setVisible(True)
            self.ui.leTd.setEnabled(True)
            self.ui.leTd.setVisible(True)
            self.ui.dsba.setVisible(True)
        self._refresh_status_bar(True)

    def _params_changed(self):
        ''' params changed '''
        self._refresh_status_bar(True)

    def _refresh_status_bar(self, needs_refresh):
        """update status bar"""
        if (needs_refresh):
            msg = "    Status : %s" % 'Refresh is needed...'
            self.ui.statusbar.setStyleSheet('QLabel {background-color : gray; color : yellow;}')
        else:
            msg = "    Status : %s" % 'OK'
            self.ui.statusbar.setStyleSheet('QLabel {background-color : green; color : white;}')
        self._status_text.setText(msg)

    def _set_PID_params(self):
        ''' set PID params for predefined PIDs '''
        self._logger.info("Gain : %.2f, Tc : %.2f, Dead Time : %.2f,Lambda value : %.2f" % (self.gain, self.tau, self.dead_time, self.lambda_tau))
        if (self.ui.cmbProccess.currentText() == "First order"):
            _method = PIDRecipe.PID_METHODS_TYPES_FODT[self.ui.cmbTuneMethod.currentIndex()]
            _method_str = self.ui.cmbTuneMethod.currentText()
            _type = _method[self.ui.cmbPIDType.currentIndex()]
            if (_method_str == "Manual" ):
                _kc, _ti, _td = float(self.ui.leKc.text()), float(self.ui.leTi.text()), float(self.ui.leTd.text())
            elif (_method_str == "Lambda" or _method_str == "IMC"):
                _kc, _ti, _td = PIDRecipe.PID_RECIPIES_FODT[self.ui.cmbTuneMethod.currentIndex()](_type, self.gain, self.tau, self.dead_time, self.lambda_tau)
                self.ui.leLambdaTauRatio.setText('{:.4}'.format(self.lambda_tau / self.tau))
            else:
                _kc, _ti, _td = PIDRecipe.PID_RECIPIES_FODT[self.ui.cmbTuneMethod.currentIndex()](_type, self.gain, self.tau, self.dead_time)
        elif (self.ui.cmbProccess.currentText() == "Integrating"):
            _method = PIDRecipe.PID_METHODS_TYPES_I[self.ui.cmbTuneMethod.currentIndex()]
            _method_str = self.ui.cmbTuneMethod.currentText()
            _type = _method[self.ui.cmbPIDType.currentIndex()]
            if (_method_str == "Manual" ):
                _kc, _ti, _td = float(self.ui.leKc.text()), float(self.ui.leTi.text()), float(self.ui.leTd.text())
            elif (_method_str == "Lambda" or _method_str == "IMC"):
                self.ui.leLambdaTauRatio.setText('0.0')
                _kc, _ti, _td = PIDRecipe.PID_RECIPIES_I[self.ui.cmbTuneMethod.currentIndex()](_type, self.gain, None, self.dead_time, self.lambda_tau)
        self.ui.leKc.setText('{:.4}'.format(_kc))
        self.ui.leTi.setText('{:.4}'.format(_ti))
        self.ui.leTd.setText('{:.4}'.format(_td))
        self.kc = _kc
        self.ti = _ti
        self.td = _td

    def _proc_step_imp_resp(self):
        '''proccess step - impulse response'''
        if (self._proc_tf):
            self._proc_step_plot.del_curves()
            t, y = control.step_response(self._proc_tf)
            self._proc_step_plot.add_curve(t, y, 'Step', 'b')
            #, y = control.impulse_response(self._proc_tf)
            #self._proc_step_plot.add_curve(t, y, 'Impulse', 'r')
            self._proc_step_plot.show()
            self._logger.info("Proccess Time Graphs opened.")
        else:
            self._logger.warning("Proccess Time Graphs failed > Invalid Proccess Model.")
            Utils.errorMessageBox("Invalid Proccess Model")

    def _cl_step_imp_resp(self):
        '''closed loop step - impulse response'''
        self._cl_step_plot.del_curves()
        if (self._proc_tf and self._pid_tf):
            self._cl_tf = control.feedback(self._proc_tf * self._pid_tf)
            t, y = control.step_response(self._cl_tf)
            self._cl_step_plot.add_curve(t, y, 'Step', 'b')
            #t, y = control.impulse_response(self._cl_tf)
            #self._cl_step_plot.add_curve(t, y, 'Impulse', 'r')
            self._cl_step_plot.show()
            self._logger.info("Closed Loop Time Graphs opened.")
        else:
            self._logger.warning("Closed Loop Time Graphs failed > Invalid Closed Loop Model.")
            Utils.errorMessageBox("Invalid Closed Loop Model")

    def _open_help_file(self):
        '''open help file'''
        _path = os.path.dirname(sys.argv[0])
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("file:///" + _path + "/PIDTuneMethods.html"))

    def closeEvent(self,QCloseEvent):
        """window is closing"""
        self._proc_step_plot.plot_dlg.close()
        self._cl_step_plot.plot_dlg.close()

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def main():

    #create logger
    logger = Utils.create_logger(logger_name='PIDTuneMethodsLog', level=logging.DEBUG)
    Utils.set_up_logger_file(logger, 'pyPIDTuneMethods.log')
    #create qt application
    app=QtWidgets.QApplication(sys.argv)
    #load main window
    w = PIDTuneMethodsWindow()
    #application loop
    res = sys.exit(app.exec_())
    #application loop quited

if __name__ == '__main__':
    main()
#-------------------------------------------------------------------------------