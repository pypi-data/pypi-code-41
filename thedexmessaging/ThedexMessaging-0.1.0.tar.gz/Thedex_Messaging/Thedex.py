from datetime import datetime


class thedexObject(object):
    CONST_CONFIG_TITLE = ""

    def getAttributesFormatted(self):
        confString = ""
        for key in vars(self):
            value = self.__getattribute__(key)

            if key[:2] == "__" \
                    or key[:6] == "CONST_" \
                    or value == "":
                continue
            confString += "{key} = {value}\n".format(key=key, value=value)
        if not confString == "":
            return "[{title}]\n".format(title=self.CONST_CONFIG_TITLE) + confString + "\n"
        else:
            return ""


class ClientData(thedexObject):
    CONST_CONFIG_TITLE = "Client"
    CONST_CONFIG_TITLE_NEW_DATA = "ClientNewData"

    CONST_INSURANCE_STATUS_MITGLIED = 1
    CONST_INSURANCE_STATUS_ANGEHOERIGER = 3
    CONST_INSURANCE_STATUS_RENTNER = 5
    CONST_INSURANCE_STATUS_VERSORGUNGSLEISTUNG = 6
    CONST_INSURANCE_STATUS_ARBEITSUNFALL = 7
    CONST_INSURANCE_STATUS_PRIVAT = "P"

    CONST_SEX_M = "M"
    CONST_SEX_F = "W"

    CSenderInternalIdentification = ""
    CExternalIdentification = ""
    CTitle = ""
    CLastName = ""
    CBirthday = ""
    CFirstName = ""
    CSex = ""
    CHeight = ""
    CWeight = ""
    CStreet = ""
    CZip = ""
    CTown = ""
    CCountryCode = ""
    CCountry = ""
    CTelephone = ""
    CFax = ""
    CCheckInID = ""
    InsuranceID = ""
    InsuranceClientID = ""
    InsuranceStatus = ""
    InsuranceDebitnumber = ""
    ClinicDepartment = ""
    ClinicRoomNumber = ""
    ClinicCaseNumber = ""
    CustomerAccount = ""
    eMail = ""
    CellularPhone = ""
    CBankIdendificationCode = ""
    CBankName: ""
    CAccountNumber: ""
    CAlternativeAccountHolder: ""
    CIBAN = ""
    CBIC = ""


class ContractData(thedexObject):
    CONST_CONFIG_TITLE = "ContractData"

    BeginDate = ""
    EndDate = ""
    TerminationDate = ""
    SuspendBeginDate = ""
    SuspendEndDate = ""
    Description = ""


class ReportData(thedexObject):
    CONST_CONFIG_TITLE = "ReportData"

    ReportDate = ""
    ReportTime = ""
    ReportDescription = ""
    ReportTherapist = ""
    ReportType = ""
    ReportFile = ""


class CheckInOutData(thedexObject):
    CONST_CONFIG_TITLE = "CheckInOutData"

    CONST_CHECK_IN_OUT_EVENT_IN = "IN"
    CONST_CHECK_IN_OUT_EVENT_OUT = "OUT"

    Event = ""
    CheckInDate = ""
    CheckInTime = ""
    CheckOutDate = ""
    CheckOutTime = ""


class Sender(thedexObject):
    CONST_CONFIG_TITLE = "Sender"

    SenderIdentification = ""
    SenderVerification = ""
    SenderDescription = ""
    SenderSoftwareVersionInformation = ""
    SenderLanIdentification = ""

    def __init__(self, senderIdentification, senderVerification) -> None:
        super().__init__()
        self.SenderIdentification = senderIdentification
        self.SenderVerification = senderVerification


class Message(thedexObject):
    CONST_CONFIG_TITLE = "Message"
    CONST_MESSAGE_TYPE_CLIENT_NEW = "ClientNew"
    CONST_MESSAGE_TYPE_CLIENT_CHANGE = "ClientChange"
    CONST_MESSAGE_TYPE_CLIENT_DELETE = "ClientDelete"
    CONST_MESSAGE_TYPE_CLIENT_REPORT = "ClientReport"
    CONST_MESSAGE_TYPE_CLIENT_INFO = "ClientInfo"
    CONST_MESSAGE_TYPE_CLIENT_CHECK_IN_OUT = "ClientCheckInOut"
    CONST_CODE_ANSI = "ANSI"
    CONST_CODE_DOS = "OEM"

    MessageType = ""
    MessageCountryInformation = ""
    MessageCodePageInformation = ""
    MessageDate = ""
    MessageTime = ""

    def __init__(self, messageType, dateTime: datetime = datetime.now()) -> None:
        super().__init__()
        self.MessageType = messageType
        self.MessageDate = dateTime.strftime("%d%m%Y")
        self.MessageTime = dateTime.strftime("%H:%M")
        self.MessageCodePageInformation = Message.CONST_CODE_ANSI


class Thedex(thedexObject):
    CONST_CONFIG_TITLE = "Thedex_Messaging"
    ThedexVersionNumber = ""

    def __init__(self) -> None:
        super().__init__()
        self.ThedexVersionNumber = "2.1"


class ThedexMessageBuilder():

    def __init__(self) -> None:
        super().__init__()


    @staticmethod
    def newClientMessage(
            sender: Sender,
            client: ClientData,
            writeFile=None,
            message: Message = Message(Message.CONST_MESSAGE_TYPE_CLIENT_NEW),
            thedex: Thedex = Thedex()
    ):
        conf = ""
        conf += thedex.getAttributesFormatted()
        conf += sender.getAttributesFormatted()
        conf += message.getAttributesFormatted()
        conf += client.getAttributesFormatted()

        if writeFile:
            with open(writeFile, 'w+') as file:
                file.write(conf)
                file.close()
        return conf
