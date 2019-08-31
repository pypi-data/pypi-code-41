import sys
import getopt
import re
import codecs
import datetime
import xlsxwriter

LOG_TAG = "[LOG_CHECK "

PlaybackStarted = "PlaybackStarted"
PlaybackNearlyFinished = "PlaybackNearlyFinished"
PlaybackFinished = "PlaybackFinished"
ProgressReportDelayElapsed = "ProgressReportDelayElapsed"
ProgressReportIntervalElapsed = "ProgressReportIntervalElapsed"
RecognizeStart = "Recognize"
RecognizeFinish = ""
StopCapture = "StopCapture"
PlaybackStopped = "PlaybackStopped"
SpeechFinished = "SpeechFinished"
SpeechStarted = "SpeechStarted"
EventResponse = ""

DateMaxLength = 0
NameMaxLength = 0
TokenMaxLength = 0

# [2019-08-09 01:52:23 ~ 00:09:14.290]

class ParseEventObj:
    def __init__(self, log, key):
        self.log = log
        self.messageId = ""
        self.offset = 0
        self.name = key
        self.date = None
        self.token = ""

        if self.name == "RecognizeStart":
            self.parseRecognizer()
        else:
            self.parse()

        if self.name == "SpeechStarted" or self.name == "SpeechFinished":
            self.token = ""

    def parse(self):
        date_m = re.search(r'\d+-\d+-\d+ \d+:\d+:\d+.*~ \d+:\d+:\d+.\d+', self.log)
        self.date = date_m.group(0)

        messageID_m = re.search(r'(?<=messageId": ").*?(?=")', self.log)
        if messageID_m:
            self.messageId = messageID_m.group(0)

        offset_m = re.search(r'(?<=offsetInMilliseconds": ).*?(?= })', self.log)
        if offset_m:
           self.offset = offset_m.group(0)
           if "-" in self.offset:
               self.offset = 0

        token_m = re.search(r'(?<=token": ").*?(?=")', self.log)
        if token_m:
            self.token = token_m.group(0)
            self.token = self.token.replace("\"", "")

    # [ { "header": { "namespace": "AudioPlayer", "name": "PlaybackState" }, "payload": { "token": "", "offsetInMilliseconds": 0, "playerActivity": "IDLE" } }
    def parseRecognizer(self):
        self.parse()
        audioplayer_m = re.search(r'context.*?\"namespace\": \"AudioPlayer\".*?{ \"header\":', self.log)
        audioplayer = audioplayer_m.group(0)
        offset_m = re.search(r'(?<=offsetInMilliseconds": ).*?(?=,)', audioplayer)
        self.offset = offset_m.group(0)

        token_m = re.search(r'(?<=token": ").*(?=",)', audioplayer)
        if token_m:
            self.token = token_m.group(0)
            self.token = self.token.replace("\"", "")

class WiFiExportCSV:
    def __init__(self, path):
        self.path = path

    def catchLog(self):
        logArray = []
        with codecs.open(self.path, "r", "utf-8", errors="ignore") as f:
            content = f.readlines()
            logObj = ""
            for line in content:
                date_m = re.search(r'\d+-\d+-\d+ \d+:\d+:\d+.*?LOG_CHECK', line)
                if date_m:
                    if len(logObj) != 0 and logObj:
                        logArray.append(logObj)
                    logObj = line

        eventsArray = []
        for line in logArray:
            parseObj = None
            if LOG_TAG in line:
                if PlaybackStarted in line:
                    parseObj = ParseEventObj(line, PlaybackStarted)

                if ProgressReportDelayElapsed in line:
                        parseObj = ParseEventObj(line, "ProgressReportDelayElapsed")

                if PlaybackStopped in line:
                    parseObj = ParseEventObj(line, "PlaybackStopped")

                if ProgressReportIntervalElapsed in line:
                    parseObj = ParseEventObj(line, "ProgressReportIntervalElapsed")

                if PlaybackNearlyFinished in line:
                    parseObj = ParseEventObj(line, "PlaybackNearlyFinished")

                if PlaybackFinished in line:
                    parseObj = ParseEventObj(line, "PlaybackFinished")

                if SpeechStarted in line:
                    parseObj = ParseEventObj(line, "SpeechStarted")

                if SpeechFinished in line:
                    parseObj = ParseEventObj(line, "SpeechFinished")

                if "[LOG_CHECK (Recognize)]" in line:
                    parseObj = ParseEventObj(line, "RecognizeStart")

                if parseObj:
                    eventsArray.append(parseObj)

        return eventsArray

    def set_column_width(self, items, worksheet):
        dateLengths = []
        nameLengths = []
        tokenLengths = []
        for item in items:
            if type(item.date) is None:
                dateLengths.append(0)
            else:
                dateStr = str(item.date)
                dateLengths.append(len(dateStr) * 1.1)

        for item in items:
            if type(item.token) is None:
                tokenLengths.append(0)
            else:
                tokenStr = str(item.token)
                tokenLengths.append(len(tokenStr) * 1.1)

        for item in items:
            if type(item.name) is None:
                nameLengths.append(0)
            else:
                nameStr = str(item.name)
                nameLengths.append(len(nameStr))

        DateMaxLength = max(dateLengths)
        NameMaxLength = max(nameLengths)
        TokenMaxLength = max(tokenLengths)
        print(DateMaxLength)
        print(NameMaxLength)
        print(TokenMaxLength)
        worksheet.set_column(0, 0, int(DateMaxLength))
        worksheet.set_column(1, 1, int(NameMaxLength))
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, int(TokenMaxLength))

    def exportReport(self, logs):
        timeStr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        path = 'Temp/WiFi_%s.xlsx' % timeStr
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0
        worksheet.write(0, col, 'Date')
        worksheet.write(0, col + 1, "Event Name")
        worksheet.write(0, col + 2, "Offset")
        worksheet.write(0, col + 3, "Token")

        for log in logs:
            row = row + 1
            worksheet.write(row, col, log.date)
            worksheet.write(row, col + 1, log.name)
            if hasattr(log, 'offset'):
                worksheet.write(row, col + 2, float(log.offset))
            if hasattr(log, 'token'):
                worksheet.write(row, col + 3, log.token)

        self.set_column_width(logs, worksheet)

        workbook.close()

        return path

if __name__ == "__main__":
    filePath = ""
    opts, args = getopt.getopt(sys.argv[1:], 'f:t:s:e:', '')
    for option, value in opts:
        if option == "-f":
            filePath = value

    if len(filePath) > 0:
        WiFiExport = WiFiExportCSV(filePath)
        events = WiFiExport.catchLog()
        path = WiFiExport.exportReport(events)
        print(path)

