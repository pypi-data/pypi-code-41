import time
import traceback

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from DynamicWebParse.RequestXPath import RequestXPath


class Requests():
    def __init__(self, dynamicWebParse):
        self.__requestsFactory = RequestXPath()
        self.__dynamicWebParse = dynamicWebParse

    def getDynamicWebParse(self):
        return self.__dynamicWebParse.getDriver()

    def actionChainsToElem(self, action, elem):
        act = action(elem)
        act.perform()

    def moveToElem(self, elem):
        self.actionChainsToElem(ActionChains(self.__dynamicWebParse.getDriver()).move_to_element, elem)

    def setFactoryXPath(self):
        self.__requestsFactory = RequestXPath()

    def WaitHaveElem(self, getData, param, load, breakTime=None):
        while True:
            startTime = time.time()
            try:
                if self.getElem(getData, breakTime=breakTime)[param] == load:
                    break
                if time.time() - startTime > breakTime:
                    break
            except:
                break


    def getElem(self, getData, breakTime=None):
        return self.__requestsFactory.getElem(getData, self.__dynamicWebParse.getDriver(), breakTime)

    def getElems(self, getData, breakTime=None):
        return self.__requestsFactory.getElems(getData, self.__dynamicWebParse.getDriver(), breakTime)

    def clickElem(self, getData, breakTime=None):
        return self.__requestsFactory.clickElem(getData, self.__dynamicWebParse.getDriver(), breakTime)

    def submitElem(self, getData, breakTime=None):
        elem = self.__requestsFactory.getElem(getData, self.__dynamicWebParse.getDriver(), breakTime)
        if not isinstance(elem, bool):
            elem.submit()

    def clickElems(self, getData, breakTime=None):
        return self.__requestsFactory.clickElems(getData, self.__dynamicWebParse.getDriver(), breakTime)

    def clickExistElems(self, elems):
        try:
            for elem in elems:
                elem.click()
            return True
        except Exception as e:
            print(e)
            return False

    def notNecessaryClick(self, getData, breakTime=None):
        return self.__requestsFactory.notNecessarlyClick(getData, self.__dynamicWebParse.getDriver(), breakTime)

    def allwaysLoadPage(self, url, timeWait=60, sleepTime=120):
        while True:
            try:
                self.__dynamicWebParse.getDriver().set_page_load_timeout(timeWait)

                self.__dynamicWebParse.getDriver().get(url)
                break
            except:
                print('TIMEOUT:\n', traceback.format_exc())
                time.sleep(sleepTime)

    def sendKeysElem(self, elem, keys):
        elem.send_keys(keys)

    def sendKeysGetElem(self, getData, keys):
        self.getElem(getData).send_keys(keys)

    def getAllElemsParam(self, param, getData, breakTime=None):
        result = list()
        for elem in self.getElems(getData, breakTime):
            result.append(elem[param])
        return result



def clickGetElemCtrl(driver, get):
    startTime = time.time()
    while True:
        try:
            elem = driver.find_element_by_xpath(get)
            elem.send_keys(Keys.COMMAND + 't')
            elem.send_keys(Keys.ENTER)
            break
        except:
            if time.time() - startTime > 5:
                print('Ошибка:\n', traceback.format_exc())
                print('stop')
                return False
            continue
    return True
