import sys
import os
import serial
import serial.tools.list_ports

import datetime
import csv
import numpy

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer,QTime,QDateTime,Qt,QSize
import pyqtgraph as pg

from presence_walkSpeed_0 import Ui_Form
class walk_speed_tool (QWidget, Ui_Form):
    def __init__(self):
        super(walk_speed_tool, self).__init__()
        self.init_plot()
        self.setupUi(self)
        self.setWindowTitle("Wanshih Walk Speed Tool Graphic User Interface")

        self.ser = serial.Serial()
        self.serial_data = 0
        self.port_check()

        self.function_init()
        self.analyze_idx = 0

    def function_init(self):
        self.s1_bt_1.clicked.connect(self.port_check)
        self.s1_bt_2.clicked.connect(self.port_open)
        self.s1_bt_3.clicked.connect(self.port_close)
        self.s1_com_1.currentTextChanged.connect(self.port_imf)

        self.s2_bt_1.clicked.connect(self.prepare_record)
        self.s2_bt_2.clicked.connect(self.record_stop)
        self.s2_bt_3.clicked.connect(self.record_export)

        self.recv_timer = QTimer(self)
        self.recv_timer.timeout.connect(self.data_receive)

        self.prepare_timer = QTimer(self)
        self.prepare_timer.setSingleShot(True)
        self.prepare_timer.timeout.connect(self.record_start)

        self.analyze_timer = QTimer(self)
        self.analyze_timer.timeout.connect(self.analyze_data)

        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self.real_time_update)

        self.sys_timer.start(200)
    def init_plot(self):
        pg.setConfigOption('background', '#f0f0f0')  # 设置背景为灰色
        pg.setConfigOption('foreground', 'd')  # 设置前景（包括坐标轴，线条，文本等等）为黑色。
        pg.setConfigOptions(antialias=True)  # 使曲线看起来更光滑，而不是锯齿状


    def port_check(self):
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1_com_1.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1_com_1.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.s1_lb_1.setText("無串口")

    def port_imf(self):
        s_imf = self.s1_com_1.currentText()
        if s_imf != "":
            self.s1_lb_1.setText(self.Com_Dict[self.s1_com_1.currentText()])
    def port_open(self):
        print("in port open")
        self.ser.port = self.s1_com_1.currentText()
        self.ser.baudrate = 1228800
        self.ser.bytesize = 8
        self.ser.stopbits = 1
        self.ser.parity = "N"

        try:
            float(self.s2_line_2.text())
        except:
            QMessageBox.critical(self, "Config Error", "請設置有效底端距離！")
            return None

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此裝置無法開啟！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.recv_timer.start(2)

        if self.ser.isOpen():
            self.s1_lb_1.setText("串口狀態：已開啟")

    def prepare_record(self):
        self.prepare_timer.start(int(self.s2_com_1.currentText())*1000)
        info = self.s2_com_1.currentText()+" "+"sec before start to record"
        self.s2_line_info.setText(info)

        self.s2_line_3.setText(self.s1_line_2.text())
        defaultName = self.s1_line_1.text()+"_"+self.s1_line_2.text()
        defaultName = defaultName.replace(":","-").replace(" ","_")+'.csv'
        self.s2_line_1.setText(defaultName)

    def record_start(self):
        self.s2_line_info.setText("recording...")
        self.analyze_timer.start(200)


    def record_stop(self):
        self.s2_line_info.setText("record finish(please press to export record)")
        self.analyze_timer.stop()
        self.s2_line_4.setText(self.s1_line_2.text())

    def record_export(self):
        self.s2_plot.clear()
        self.s2_plot_2.clear()


        self.s2_t2_browser.setText("")

        with open('fileRaw.csv',newline='') as fileIn:
            r = csv.reader(fileIn)
            data = [line for line in r]
            fileName = self.s2_line_1.text()

            with open(fileName, 'w', newline='') as fileOut:
                w = csv.writer(fileOut)
                w.writerow(['timeStamp', 'locat'])
                w.writerows(data)

        timeList = []
        locatList = []
        reg_timeList =[]
        reg_locatList = []
        with open(fileName, newline='') as csvfile:
            rows = csv.DictReader(csvfile)
            for oneRow in rows:
                timeList.append(oneRow['timeStamp'])
                locatList.append(float(oneRow['locat']))

            print(len(locatList))
            print(max(locatList))

        locatPlot_widget = self.s2_plot.addPlot()
        locatPlot_widget.setXRange(0, len(locatList), padding=0)
        locatPlot_widget.setYRange(0, max(locatList)+2, padding=0)

        font = QFont()
        font.setPixelSize(12)
        locatPlot_widget.getAxis('left').tickFont = font
        locatPlot_widget.getAxis('bottom').tickFont = font

        locatPlot_widget.setLabel('left', ' ', units='Unit : Meter ', **{'color': '#000', 'font-size': '12pt'})
        locatPlot_widget.setLabel('bottom', ' ', units=' Unit : 0.2 sec', **{'color': '#000', 'font-size': '12pt'})

        locatPlot_scatter = pg.ScatterPlotItem(pen=pg.mkPen(None))

        for x in range(0, len(locatList)):
            if locatList[x] == 0:
                pass
            else:
                reg_timeList.append(x)
                reg_locatList.append(locatList[x])
                try:
                    xdata = x
                    ydata = locatList[x]
                    color = 120
                    spots = [
                        {'pos': [xdata, ydata], 'symbol': 2, 'size': 18, 'data': 1,
                         'brush': (color + 40, 230 - color, 0, 255)}]
                    locatPlot_scatter.addPoints(spots)

                    info = "x:"+str(x)+",y:"+str(ydata)
                    print(info)

                except:
                    pass
        locatPlot_widget.addItem(locatPlot_scatter)
        self.s2_line_info.setText("in "+str(len(timeList)/5)+" sec")

        print(reg_locatList)
        print(reg_timeList)

        info = "start at "+str(max(reg_locatList))+" ,end at "+str(min(reg_locatList))+"(m)\r\n"
        startIdx= reg_timeList[reg_locatList.index(max(reg_locatList))]*(0.2)
        endIdx = reg_timeList[reg_locatList.index(min(reg_locatList))]*(0.2)
        info_2 = "start time: "+str(startIdx)+" ,end time: "+str(endIdx)+"(sec)\r\n"

        info_averageSpeed = "average speed: "+str((max(reg_locatList)-min(reg_locatList))/(endIdx-startIdx))

        self.s2_t2_browser_print(char=info)
        self.s2_t2_browser_print(char=info_2)

        self.s2_t2_lcd_1.display((max(reg_locatList)-min(reg_locatList))/(endIdx-startIdx))

        instantTimeList = []
        instantMoveList = []
        for i in range (0, len(reg_timeList)-1):
            instantTimeList.append((reg_timeList[i+1]-reg_timeList[i])*0.2)
            instantMoveList.append(reg_locatList[i]-reg_locatList[i+1])
        print(instantTimeList)
        print(instantMoveList)

        instantSpeedList = []
        for m in range(0, len(reg_timeList) - 1):
            instantSpeedList.append(instantMoveList[m]/instantTimeList[m])
        print(instantSpeedList)

        instantTimeDeltaList =[]
        for k in range(0, len(instantTimeList)):
            if k == 0:
                instantTimeDeltaList.append(instantTimeList[k])
            else:
                instantTimeDeltaList.append(instantTimeList[k]+instantTimeDeltaList[k-1])


        for j in range(0, len(instantSpeedList)):
            instantInfo = "in "+str(instantTimeDeltaList[j])+" sec"+\
                " speed:"+str(instantSpeedList[j])+"\r\n"

            self.s2_t2_browser_print(char=instantInfo)


        instanSpeedPlot = self.s2_plot_2.addPlot(title = 'instant speed')
        instanSpeedPlot.setLabel('left', ' ', units='Unit : m/s ', **{'color': '#000', 'font-size': '12pt'})
        instanSpeedPlot.setLabel('bottom', ' ', units=' Unit : 0.2 sec', **{'color': '#000', 'font-size': '12pt'})

        columnSpeedList = []
        '''
        for n in range(0, len(instantSpeedList)):
            for k in range(0, int(instantTimeList[n]*5)):
                if k == 0:
                    columnSpeedList.append(instantSpeedList[n])
                else:
                    columnSpeedList.append(0)
        '''
        for n in range(0, int(startIdx*5)):
            columnSpeedList.append(0)
        for n in range(0, len(instantSpeedList)):
            for k in range(0, int(instantTimeList[n] * 5)):
                if k == 0:
                    columnSpeedList.append(instantSpeedList[n])
                else:
                    columnSpeedList.append(0)
        for l in range(0, len(locatList)-int(endIdx*5)):
            columnSpeedList.append(0)


        instanSpeedPlot.plot(y=columnSpeedList, pen=(128, 128, 0))

        fileName_speed = "walkSpeed_"+self.s2_line_1.text()

        with open(fileName_speed, 'w', newline='') as fileOut:
            w = csv.writer(fileOut)
            w.writerow(['timeStamp', 'locat','instant speed'])
            for p in range(0, len(locatList)):
                row = [timeList[p], locatList[p], columnSpeedList[p]]
                w.writerow(row)

        try:
            os.remove('fileRaw.csv')
        except OSError as e:
            print(e)
        else:
            print("File is deleted successfully")
            self.s1_line_3.setText(self.s1_line_2.text())
    def s2_t2_browser_print(self,char=" "):
        self.s2_t2_browser.insertPlainText(char)
        textCursor = self.s2_t2_browser.textCursor()
        textCursor.movePosition(textCursor.End)
        self.s2_t2_browser.setTextCursor(textCursor)


    def port_close(self):
        self.recv_timer.stop()

        try:
            self.ser.close()
        except:
            pass
        self.s1_lb_1.setText("串口狀態：已關閉")


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

            data = self.serial_data

            if len(str(data)[14:17].replace(" ", "")) > 0:
                raw = str(data)[14:17].replace(" ", "")
                distanceValue = int(raw)
                if distanceValue >= float(self.s2_line_2.text())*100:
                    self.s1_lcd_1.display(0.00)
                else:
                    self.s1_lcd_1.display(float(distanceValue / 100))
        else:
            pass

    def analyze_data(self):
        while True:
            time_format = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
            row = [time_format,self.s1_lcd_1.value()]
            with open('fileRaw.csv','a',newline='') as file:
                wr = csv.writer(file)
                wr.writerow(row)
            break

        '''
        only for test use.我的小精靈
        self.analyze_idx = self.analyze_idx +1
        if self.analyze_idx == 5*10:
            self.record_stop()
            self.analyze_idx = 0
        '''

    def real_time_update(self):
        time_format = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.s1_line_2.setText(str(time_format))




if __name__ == "__main__":
    print("system start")
    app = QApplication(sys.argv)
    ui = walk_speed_tool()
    ui.show()
    sys.exit(app.exec_())