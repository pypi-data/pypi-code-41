import sys
import getopt
import xlrd
from datetime import datetime
from time import mktime
import time
import xlsxwriter
import re
import webbrowser
import os
import subprocess

PlaybackStarted = "PlaybackStarted"
ProgressReportDelayElapsed = "ProgressReportDelayElapsed"
ProgressReportIntervalElapsed = "ProgressReportIntervalElapsed"
PlaybackStopped = "PlaybackStopped"
PlaybackNearlyFinished = "PlaybackNearlyFinished"
PlaybackFinished = "PlaybackFinished"
RecognizeStart = "RecognizeStart"
SpeechFinished = "SpeechFinished"
SpeechStarted = "SpeechStarted"
RecognizeFinish = "RecognizeFinish"
EventResponse = "EventResponse"
PlaybackStutterStarted = "PlaybackStutterStarted"
PlaybackStutterFinished = "PlaybackStutterFinished"
StopCaptureDirective = "StopCapture"
StopDirective = "StopDirective"

class LPReportEvent:
    def __init__(self, values):
        self.date = ""
        self.name = ""
        self.offset = 0
        self.token = ""
        self.delay = 0
        self.expectOffset = 0
        self.deltaOffset = 0

        if len(values) >= 4:
            self.date = values[0]
            self.name = values[1]
            self.offset = values[2]
            self.token = values[3]

    def set_deltaOffset(self, actualOffset):
        deltaTime = float(actualOffset) - float(self.offset)/1000
        self.expectOffset = actualOffset
        self.deltaOffset = deltaTime


class LPCertReport:
    def __init__(self, path, platform,logger=None):
        self.path = path
        self.logs = []
        self.events = []
        self.platform = platform

        if logger:
            self.logger = logger

    def logger(self):
        pass

    def readXlsx(self):
        book = xlrd.open_workbook(self.path)
        sh = book.sheet_by_index(0)
        eventArray = []
        for rx in range(sh.nrows):
            if rx == 0:
                continue
            values = sh.row_values(rx)
            event = LPReportEvent(values)
            eventArray.append(event)

        self.events = eventArray

    def startParse(self):
        playbackStartedEvent = None
        playbackFinishedEvent = None
        recognizeStart = None
        recognizeFinish = None
        SpeechStartedEvent = None
        SpeechFinishedEvent = None
        latestStopCaptureDirective = None

        for event in self.events:
            if event.name == StopCaptureDirective:
                latestStopCaptureDirective = event

            # 找到第一个playback started event
            if not playbackStartedEvent:
                if event.name != PlaybackStarted:
                    continue
                else:
                    self.logger("%s:PlaybackStartedEvent:%.3f" % (event.date,  float(event.offset)/1000))
                    playbackStartedEvent = event
                    event.delay = self.playbackStartedDelay(event, playbackFinishedEvent, SpeechFinishedEvent, recognizeFinish)
                    self.logs.append(event)
                    continue
            elif event.name == PlaybackStarted:
                self.logger("%s:PlaybackStartedEvent:%.3f" % (event.date,  float(event.offset)/1000))
                playbackStartedEvent = event
                event.delay = self.playbackStartedDelay(event, playbackFinishedEvent, SpeechFinishedEvent, recognizeFinish)
                self.logs.append(event)
                continue

            offsetTime = 0
            if playbackStartedEvent:
                if event.name == ProgressReportDelayElapsed:
                    offsetTime = self.intervalTime(playbackStartedEvent, event) + float(playbackStartedEvent.offset)/1000
                    event.set_deltaOffset(offsetTime)
                    self.logger("%s:ProgressReportDelayElapsed:%.3f reportOffset:%.3f deltaTime:%f" % (event.date, offsetTime, float(event.offset)/1000, event.deltaOffset))

                if event.name == ProgressReportIntervalElapsed:
                    offsetTime = self.intervalTime(playbackStartedEvent, event) + float(playbackStartedEvent.offset)/1000
                    event.set_deltaOffset(offsetTime)
                    self.logger("%s:ProgressReportIntervalElapsed:%.3f reportOffset:%.3f" % (event.date, offsetTime, float(event.offset)/1000))

                if event.name == StopDirective:
                    event.delay = self.intervalTime(event, latestStopCaptureDirective)

                if event.name == PlaybackStopped:
                    offsetTime = self.intervalTime(playbackStartedEvent, event) + float(playbackStartedEvent.offset)/1000
                    if recognizeStart and (not recognizeFinish):
                        pass
                    event.set_deltaOffset(offsetTime)
                    # playbackStartedEvent = None
                    self.logger("%s:PlaybackStopped:%.3f reportOffset:%.3f" % (event.date, offsetTime, float(event.offset)/1000))

                if event.name == PlaybackFinished:
                    playbackFinishedEvent = event
                    offsetTime = self.intervalTime(playbackStartedEvent, event) + float(playbackStartedEvent.offset)/1000
                    event.set_deltaOffset(offsetTime)
                    self.logger("%s:playback finished offset: %.3f" % (event.date, offsetTime))

                if event.name == PlaybackNearlyFinished:
                    offsetTime = self.intervalTime(playbackStartedEvent, event) + float(playbackStartedEvent.offset)/1000
                    event.set_deltaOffset(offsetTime)
                    self.logger("%s:Playback nearly finished offset: %.3f" % (event.date, offsetTime))

                if event.name == PlaybackStutterStarted:
                    self.logger("%s:PlaybackStutterStarted" % event.date)

                if event.name == PlaybackStutterFinished:
                    self.logger("%s:PlaybackStutterFinished offset:%.3f" % (event.date, float(event.offset)/1000))

                # recognize， speech started，speech finished 之间时间
                if event.name == RecognizeStart:
                    SpeechStartedEvent = None
                    SpeechFinishedEvent = None
                    recognizeFinish = None
                    # save first recogize Start
                    if not recognizeStart:
                        recognizeDuration = 0
                        recognizeStart = event
                        self.logger("%s:Recognize start" % event.date)
                    else:
                        recognizeStart = event
                        self.logger("%s:Recognize" % event.date)

                if event.name == RecognizeFinish:
                    recognizeFinish = event
                    playbackFinishedEvent = None
                    if recognizeStart:
                        recognizeDuration = self.intervalTime(recognizeStart, recognizeFinish)
                        event.delay = self.intervalTime(latestStopCaptureDirective, event)
                        self.logger("%s:Recognize finish and duration: %.3f" % (recognizeFinish.date, recognizeDuration))
                        recognizeStart = None

                if event.name == SpeechStarted:
                    # save speech started event, don't calculate.
                    SpeechStartedEvent = event

                if event.name == SpeechFinished:
                    SpeechFinishedEvent = event
                    if recognizeFinish:
                        pass
                    elif SpeechStartedEvent:
                        pass
            self.logs.append(event)

        reportName = self.path.split("/")[-1]
        self.exportReport(self.logs, reportName)


    def playbackStartedDelay(self, playbackStarted, playbackfinished, speakFinished, recoginzeFinished):
        if playbackfinished:
            return self.intervalTime(playbackfinished, playbackStarted)
        elif speakFinished:
            return self.intervalTime(speakFinished, playbackStarted)
        elif recoginzeFinished:
            return self.intervalTime(recoginzeFinished, playbackStarted)

        return 0

    def wifiDate(self, date):
        originDate_m = re.search(r'(?<=~ )\d+:\d+:\d+.\d+', date)
        if originDate_m:
            originDate = originDate_m.group(0)
            return  originDate
        return date


    def intervalTime(self, firstEvent, secondEvent):
        if self.platform.lower() == "wifi":
            firstEventDate = self.wifiDate(firstEvent.date)
            secondEventDate = self.wifiDate(secondEvent.date)

            firstMillisecond = float(firstEventDate.split(".")[-1])/1000
            secondMillisecond = float(secondEventDate.split(".")[-1])/1000
            firstTime = time.strptime(firstEventDate, "%H:%M:%S.%f")
            firstDate = datetime.fromtimestamp(mktime(firstTime))
            secondTime = time.strptime(secondEventDate, "%H:%M:%S.%f")
            secondDate = datetime.fromtimestamp(mktime(secondTime))
            deltaTime = secondDate - firstDate
            deltaMilliseconds = deltaTime.total_seconds() + (secondMillisecond - firstMillisecond)
        else:
            # 19:27:25.419
            firstMillisecond = float(firstEvent.date.split(".")[-1])/1000
            secondMillisecond = float(secondEvent.date.split(".")[-1])/1000
            firstTime = time.strptime(firstEvent.date, "%Y-%m-%d %H:%M:%S.%f")
            firstDate = datetime.fromtimestamp(mktime(firstTime))
            secondTime = time.strptime(secondEvent.date, "%Y-%m-%d %H:%M:%S.%f")
            secondDate = datetime.fromtimestamp(mktime(secondTime))
            deltaTime = secondDate - firstDate
            deltaMilliseconds = deltaTime.total_seconds() + (secondMillisecond - firstMillisecond)
        return deltaMilliseconds

    def exportReport(self, logs, name):
        reportPath = 'Temp/Report_%s' % name
        workbook = xlsxwriter.Workbook(reportPath)
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0
        worksheet.write(0, col, 'Date')
        worksheet.write(0, col + 1, "Event Name")
        worksheet.write(0, col + 2, "Offset")
        worksheet.write(0, col + 3, "Expect Offset")
        worksheet.write(0, col + 4, "Delta Offset")
        worksheet.write(0, col + 5, "Delay")
        worksheet.write(0, col + 6, "Token")

        data_format1 = workbook.add_format({'bg_color': '#FFC7CE'})

        for log in logs:
            row = row + 1
            worksheet.write(row, col, log.date)
            worksheet.write(row, col + 1, log.name)
            if hasattr(log, 'offset'):
                worksheet.write(row, col + 2, float(log.offset)/1000)
            if hasattr(log, 'expectOffset'):
                worksheet.write(row, col + 3, log.expectOffset)
            if hasattr(log, 'deltaOffset'):
                worksheet.write(row, col + 4, log.deltaOffset)
            if hasattr(log, 'delay'):
                if self.platform.lower() == "wifi":
                    if log.name == "PlaybackStarted":
                        worksheet.write(row, col + 5, log.delay)
                else:
                    if abs(log.delay) > 4.5:
                        worksheet.set_row(row, cell_format=data_format1)
                    worksheet.write(row, col + 5, log.delay)
            if hasattr(log, 'token'):
                worksheet.write(row, col + 6, log.token)

        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 30)
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, 13)
        worksheet.set_column(4, 4, 13)
        worksheet.set_column(5, 5, 10)
        worksheet.set_column(6, 6, 100)

        workbook.close()
        self.open_file("Temp/")

    def open_file(self, filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener ="open"
            if sys.platform == "darwin":
                opener ="open"
            else:
                opener = "xdg-open"
            subprocess.call([opener, filename])

def printLogger(log):
    print(log)

if __name__ == "__main__":
    filePath = ""
    platform = ""
    opts, args = getopt.getopt(sys.argv[1:], 'f:p:s:e:', '')
    for option, value in opts:
        if option == "-f":
            filePath = value
        elif option == "-p":
            platform = value

    if len(filePath) > 0:
        certReport = LPCertReport(filePath, platform, printLogger)
        certReport.readXlsx()
        certReport.startParse()
