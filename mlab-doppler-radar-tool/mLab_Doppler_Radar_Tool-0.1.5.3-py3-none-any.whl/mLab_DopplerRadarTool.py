

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pyqtgraph as pg
#from ui_pyqtgraph_rev2 import Ui_MainWindow
from  .ui_pyqtgraph_rev2_1 import  Ui_Form
import numpy as np
import serial
import serial.tools.list_ports
import sys
import datetime
import cv2
import re
import csv

i_raw_line = np.repeat(0, 128)
x_raw_line = np.repeat(100, 128)

class MainWindow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.init_plot()


        self.setupUi(self)
        self.one_plot()
        self.setWindowTitle("Wanshih IC test Graphic User Interface")
        self.setWindowIcon(QIcon("./image/wanshih_logo.png"))

        # uart port
        self.ser = serial.Serial()
        self.port_check()
        # receive data initial
        self.serial_data = 0

        # monitor
        self.camera_num = cv2.VideoCapture(self.bt_cam.currentIndex())
        self.capture_frame = 0
        self.capture_flag = 0

        #draw plot
        self.i_raw_line = i_raw_line
        self.x_raw_line = x_raw_line
        self.speedRecordDict ={}

        self.initialize()

    def init_plot(self):
        pg.setConfigOption('background', '#f0f0f0')  # 设置背景为灰色
        pg.setConfigOption('foreground', 'd')  # 设置前景（包括坐标轴，线条，文本等等）为黑色。
        pg.setConfigOptions(antialias=True)  # 使曲线看起来更光滑，而不是锯齿状

    def one_plot(self):
        self.plot_widget.clear()

        example_plot = self.plot_widget.addPlot(title = 'XMC1302 Radar Raw data')

        global i_raw_line, x_raw_line
        y1 = i_raw_line
        y2 = x_raw_line
        self.threshold_line = np.repeat(int(self.bt_thers_set.currentText()), 128)

        example_plot.plot(y=y1, pen=(128, 128, 0))
        example_plot.plot(y=y2, pen= (128,0,0))
        example_plot.plot(y=self.threshold_line, pen=(56, 32, 22))

    def initialize(self):
        self.start_time_stamp()
        self.real_time_stamp()

        self.recv_timer = QTimer(self)
        self.recv_timer.timeout.connect(self.data_receive)
        self.analyze_timer = QTimer(self)
        self.analyze_timer.timeout.connect(self.analyze_data)

        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.monitor_check)
        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.one_plot)

        self.speed_record_timer = QTimer(self)
        self.speed_record_timer.timeout.connect(self.update_speed_record_dict)

        self.bt_cam_start.clicked.connect(self.open_cam)
        self.bt_cam_stop.clicked.connect(self.stop_cam)

        self.s1_bt_1.clicked.connect(self.port_check)
        self.s1_bt_2.currentTextChanged.connect(self.port_imf)

        self.s1_bt_5.clicked.connect(self.port_open)
        self.s1_bt_6.clicked.connect(self.port_close)

        self.s2_bt_3.clicked.connect(self.data_send)

        self.bt_start_draw.clicked.connect(self.start_draw)
        self.bt_stop_draw.clicked.connect(self.pause_draw)

        self.bt_save_data.clicked.connect(self.save_raw_data)

        self.s4_bt_3.clicked.connect(self.record_speed)
        self.s4_bt_1.clicked.connect(self.start_record)
        self.s4_bt_2.clicked.connect(self.stop_record)

        self.s4_bt_2.setDisabled(True)
        self.s4_bt_3.setDisabled(True)


    def real_time_stamp(self):
        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self.real_time_update)
        self.sys_timer.start(1000)

    def real_time_update(self):
        time_format = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.s3_line_2.setText(str(time_format))

    def start_time_stamp(self):
        time_format = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.s3_line_1.setText(str(time_format))

    def monitor_check(self):
        ret, frame = self.camera_num.read()
        if (1 == ret):
            file_name = 'capture.jpeg'
            cv2.imwrite(file_name, frame)
            pixmap = QPixmap("./capture.jpeg")

            try:
                if(1 == self.capture_flag):
                    pixmap.fill(color=Qt.red)
                    self.capture_flag = 0
                elif(2 == self.capture_flag):
                    pixmap.fill(color=Qt.darkCyan)
                    self.capture_flag = 0
            except:
                return None

        self.lb_photo.setPixmap(pixmap)

    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1_bt_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1_bt_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.s1_lb_3.setText(" 无串口")

    def port_imf(self):
        s_imf = self.s1_bt_2.currentText()
        if s_imf != "":
            self.s1_lb_3.setText(self.Com_Dict[self.s1_bt_2.currentText()])

    def port_open(self):
        self.ser.port = self.s1_bt_2.currentText()
        self.ser.baudrate = 128000
        self.ser.bytesize = 8
        self.ser.stopbits = 1
        self.ser.parity = "N"

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此裝置無法開啟！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.recv_timer.start(300)
        self.analyze_timer.start(300)

        if self.ser.isOpen():
            self.s1_bt_5.setEnabled(False)
            self.s1_bt_6.setEnabled(True)
            self.s4_line_3.setText("串口狀態：已開啟")

    def port_close(self):
        self.recv_timer.stop()
        self.analyze_timer.stop()
        try:
            self.ser.close()
        except:
            pass

        self.s1_bt_5.setEnabled(True)
        self.s1_bt_6.setEnabled(False)
        self.s4_line_3.setText("串口狀態（已關閉)")


    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None

        if num > 0:
            self.serial_data = self.ser.readline()
            #self.serial_data = self.ser.read(num)
            self.raw_broswer.insertPlainText(self.serial_data.decode('iso-8859-1'))
            textCursor = self.raw_broswer.textCursor()
            textCursor.movePosition(textCursor.End)
            self.raw_broswer.setTextCursor(textCursor)
        else:
            pass

    def data_send(self):
        MIN_STAMP = 'I'
        MXA_STAMP = 'X'
        END_STAMP = 'H8'

        if self.ser.isOpen():
            input_s = MIN_STAMP + str(self.s2_di_1.value()) + MXA_STAMP + str(self.s2_di_2.value()) + END_STAMP
            #print(input_s)
            input_s = input_s.encode('utf-8')
            self.ser.write(input_s)
        else:
            pass

        self.s2_lb_3.setText("設置最小值：%u 最大值:%u  (km/hrs)"%(self.s2_di_1.value()*2, self.s2_di_2.value()*5))

    def analyze_data(self):
        data = str(self.serial_data)
        list_start = [m.start() for m in re.finditer('@', data)]
        list_end = [m.start() for m in re.finditer('#', data)]
        list_dot = [m.start() for m in re.finditer(',', data)]

        global i_raw_line, x_raw_line

        '''
        '''

        if len(list_start) > 0:
            try:
                self.s4_line_1.display(int(data[list_dot[255] + 2:list_dot[256]])/100)
                self.s4_line_2.display(int(data[list_dot[256]+2:list_end[0]]))
                if 'a'== data[list_dot[255]+1]:
                    self.s4_line_3.setText('物體靠近')
                    self.capture_flag = 1
                elif 'b' == data[list_dot[255] + 1]:
                    self.s4_line_3.setText('物體遠離')
                    self.capture_flag = 2
                else:
                    self.s4_line_3.setText('')

            except:
                return None

            if (self.plot_timer.isActive())&(257==len(list_dot)):
                #print("complex analyze")
                try:
                    i_raw_line[0]=int(data[list_start[0]+1:list_dot[0]])
                    x_raw_line[0]=int(data[list_dot[127]+1:list_dot[128]])

                    for i in range (1, 128):
                        i_raw_line[i] = int(data[list_dot[i]+1:list_dot[i+1]])
                        x_raw_line[i] = int(data[list_dot[i+127] + 1:list_dot[i +127 +1]])

                except:
                    return None

    def open_cam(self):
        self.monitor_timer.start(100)
        self.s4_line_3.setText("攝影機狀態（已開啟)")
        self.bt_cam_start.setEnabled(False)
        self.bt_cam_stop.setEnabled(True)

    def stop_cam(self):
        self.monitor_timer.stop()
        self.s4_line_3.setText("攝影機狀態（已關閉)")
        self.bt_cam_stop.setEnabled(False)
        self.bt_cam_start.setEnabled(True)

    def start_draw(self):
        self.plot_timer.start(300)
        self.s4_line_3.setText("raw data plot start")
        self.bt_start_draw.setEnabled(False)
        self.bt_stop_draw.setEnabled(True)
        self.bt_save_data.setEnabled(False)

    def pause_draw(self):
        self.plot_timer.stop()
        self.s4_line_3.setText("raw data plot pause")
        self.bt_start_draw.setEnabled(True)
        self.bt_stop_draw.setEnabled(False)
        self.bt_save_data.setEnabled(True)

    def save_raw_data(self):
        global i_raw_line, x_raw_line
        with open('output.csv','w',newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(i_raw_line)
            writer.writerow(x_raw_line)
    def start_record(self):
        self.speed_record_timer.start(250)

        self.s4_bt_1.setDisabled(True)
        self.s4_bt_2.setDisabled(False)
        self.s4_bt_3.setDisabled(True)

    def stop_record(self):
        self.speed_record_timer.stop()

        self.s4_bt_1.setDisabled(False)
        self.s4_bt_2.setDisabled(True)
        self.s4_bt_3.setDisabled(False)

    def record_speed(self):

        fileName = str(list(self.speedRecordDict.keys())[-1]).replace(":","_")+'.csv'

        csv=  open(fileName, 'a')
        columnTitleRow = "time, speed\n"
        csv.write(columnTitleRow)
        for key in self.speedRecordDict.keys():
            time= key
            speed = self.speedRecordDict[key]
            row = time+","+speed+"\n"
            csv.write(row)

        self.speedRecordDict.clear()

        self.s4_bt_1.setDisabled(False)
        self.s4_bt_2.setDisabled(True)
        self.s4_bt_3.setDisabled(True)

    def update_speed_record_dict(self):
        time = QTime.currentTime()
        self.speedRecordDict.update({time.toString('hh:mm:ss:zzz'): str(self.s4_line_1.value())})






if __name__ == "__main__":
    print("system start")
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())