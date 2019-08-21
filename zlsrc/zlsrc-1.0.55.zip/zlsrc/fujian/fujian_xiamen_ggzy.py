import random
from collections import OrderedDict
from math import ceil

import pandas as pd
import re
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlsrc.util.fake_useragent import UserAgent
import sys
import time
import json
from zlsrc.util.etl import est_html, est_meta_large, add_info


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}
    url = driver.current_url
    if "getMongoGovPurchaseNoticePage.do/" in url:
        payloadData = payload_Data(url, num)
        url = url.rsplit('/', maxsplit=1)[0]
    else:
        payloadData = payload_Data(url, num)
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        # 'Cookie': cookiestr,
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        'Host': 'zyjy.xmas.gov.cn',
    }
    res = requests.post(url=url, headers=headers, data=json.dumps(payloadData),proxies=proxies)
    # 需要判断是否为登录后的页面
    data_list = []
    time.sleep(2)
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            if "getMongoGovPurchaseNoticePage.do" in url:
                html = json.loads(html)
                data = html["data"]
                datalist = data["datalist"]
                for data in datalist:
                    projName = data['projName']
                    publishTime = data['publishTime']
                    link = "http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/governBid.do?noticeId=" + data['noticeId'] + "&noticeType=" +\
                           "{}".format(noticeType) + "&projCode=" + data['projCode'] + "&projId=" + data['projId']

                    diqu = data['areaCode']
                    xm_num = data['projCode']
                    zb_type = data['organizeForm']
                    info = json.dumps({'diqu':diqu,'xm_num':xm_num,'zb_type':zb_type}, ensure_ascii=False)
                    tmp = [projName, publishTime, link, info]
                    data_list.append(tmp)
            else:
                html = json.loads(html)
                data = html["data"]
                datalist = data["dataList"]
                for data in datalist:
                    if "getConstructInfoPage.do" in url:
                        projName = data['projName']
                        pubDate = data['recordDate']
                        link = "http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/registerInfo.do?" + "projId=" + data['projId'] + "&dataFrom=" + str(data['dataFrom'])
                        bj_num = data['projCode']
                        info = json.dumps({'bj_num':bj_num}, ensure_ascii=False)
                    elif "/getNoticePage.do" in url:
                        projName = data['projName']
                        pubDate = data['SEND_TIM']
                        link = "http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/agentBid.do?leftIndex=F006" + "&uniqueId=" + data['uniqueId']
                        xm_num = data['tenderProjCode']
                        hy_type = data['tenderProjType']
                        info = json.dumps({'xm_num': xm_num, 'hy_type':hy_type}, ensure_ascii=False)
                    else:
                        leftIndex = ""
                        if "getBltPage.do" in url:
                            leftIndex = "leftIndex=F001"
                        elif "getAnQuestionPage_project.do" in url:
                            leftIndex = "leftIndex=F002"
                        elif "getEvaBulletinPage.do" in url:
                            leftIndex = "leftIndex=F004"
                        elif "getwinBulletinPage_project.do" in url:
                            leftIndex = "leftIndex=F005"
                        projName = data['projName']
                        try:
                            pubDate = data['pubDate']
                        except:
                            pubDate = data['sendTime']

                        xm_num = data['tenderProjCode']
                        hy_type = data['tenderProjType']
                        info = json.dumps({'xm_num': xm_num, 'hy_type': hy_type}, ensure_ascii=False)
                        link = "http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/agentBid.do?" + leftIndex + "&uniqueId=" + data['uniqueId'] + "&objId=" + data['bid']
                    tmp = [projName, pubDate, link, info]
                    data_list.append(tmp)
    df = pd.DataFrame(data_list)
    return df


def payload_Data(url, num):
    if "getMongoGovPurchaseNoticePage.do/" in url:
        global noticeType
        noticeType = re.findall(r'/(\d+)', url)[0]
        payloadData = {'pageIndex': "{}".format(num), 'pageSize': "10", 'noticeTitle': "", 'regionCode': "", 'tenderType': "D", 'transType': "", 'pubTime': "",
                       'state': "", 'noticeType': "{}".format(noticeType), 'purchaseType': "", 'searchBeginTime': "", 'searchEndTime': ""}
        return payloadData
    elif "getConstructInfoPage.do" in url:
        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'classId':0,'centerId':0,'projNo':"",'projName':"",'ownerDeptName':"",'showRange':"",'searchBeginTime':"",'searchEndTime':""}
    elif "getNoticePage.do" in url:
        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'centerId':0,'projName':"",'title':"",'showRange':""}
    else:
        payloadData = {'pageIndex': "{}".format(num), 'pageSize': "10", 'projName': "", 'centerId': 0, 'showRange': "",'tenderProjType': "", 'searchBeginTime': "", 'searchEndTime': ""}

    return payloadData


def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}
    url = driver.current_url
    payloadData = payload_Data(url, 1)
    if "getMongoGovPurchaseNoticePage.do/" in url:
        url = url.rsplit('/', maxsplit=1)[0]
    num = get_pageall(url, payloadData,proxies)

    driver.quit()
    return num


def get_pageall(url, payloadData,proxies):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        'Host': 'zyjy.xmas.gov.cn',
        }
    res = requests.post(url=url, headers=headers, data=json.dumps(payloadData),proxies=proxies)
    # 需要判断是否为登录后的页面
    # datas = []
    # print(res)
    time.sleep(2)
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            if "getMongoGovPurchaseNoticePage.do" in url:
                html = json.loads(html)
                data = html["data"]
                total = int(data["pagecount"])
                page_all = ceil(total / 10)
                return page_all
            else:
                html = json.loads(html)
                data = html["data"]
                total = int(data["totalPage"])
                return total


def f3(driver, url):
    driver.get(url)
    if "/xmebid/governBid.do?" in url:
        locator = (By.XPATH, "//div[@id='tenderNoticeContent'][string-length()>150]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(0.1)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find('div', id="tenderNoticeContent")
        return div
    elif "/xmebid/registerInfo.do?" in url:
        locator = (By.XPATH, "//table[@class='hasBorder'][string-length()>150]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(0.1)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find('div', style="margin: 30px 30px 5px 30px;")
        return div
    else:
        locator = (By.XPATH, "//div[@id='main'][string-length()>400]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        fl2 = OrderedDict([('F001', '招标公告'), ('F002', '招标答疑'), ('F003', '工程控制价'),
                           ('F004', '中标候选人公示'), ('F005', '中标结果公示'), ('F006', '通知公告')])
        flag = re.findall(r'leftIndex=(.*?)&', url)[-1]
        locator = (By.XPATH, "//div[@id='main'][string-length()>400]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH,
                   "//span[@id='noticeTitleName'][contains(string(), '%s')] | //span[@id='noticeTitle'][contains(string(), '%s')]" % (fl2[flag], fl2[flag]))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        time.sleep(random.uniform(1, 2))
        before = len(driver.page_source)
        time.sleep(0.5)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(0.5)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        if 'class="emptyNotice"' in page:
            return '暂无发布内容'
        elif 'id="iframepage"' in page:
            soup = BeautifulSoup(page, 'html.parser')
            div1 = soup.find('div', class_="details_content")
            div2 = get_iframe_data(driver)
            div = str(div1) + str(div2)
            div = BeautifulSoup(div, 'html.parser')
            return div
        else:
            soup = BeautifulSoup(page, 'html.parser')
            div = soup.find('div', class_="details_content")
            return div


def get_iframe_data(driver):
    locator = (By.XPATH, "//iframe[@id='iframepage']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    driver.switch_to_frame('iframepage')
    try:
        locator = (By.XPATH, "//embed[@id='plugin'] | (//div[@class='textLayer'])[last()][string-length()>50]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        if not re.findall('class="Section\d*"',driver.page_source) :
            locator = (By.XPATH, "//embed[@id='plugin'] | (//div[@class='textLayer'])[last()-1][string-length()>50]")
            WebDriverWait(driver, 2).until(EC.presence_of_element_located(locator))
        else:
            locator = (By.XPATH, "//div[contains(@class,'Section')][string-length()>150]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            before = len(driver.page_source)
            time.sleep(1)
            after = len(driver.page_source)
            i = 0
            while before != after:
                before = len(driver.page_source)
                time.sleep(0.5)
                after = len(driver.page_source)
                i += 1
                if i > 5: break
            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            div = soup.find('div', class_=re.compile("Section\d*"))
            return div

    locator = (By.XPATH, '//input[@id="pageNumber"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    tnum = driver.find_element_by_xpath('//span[@id="numPages"]').text.strip()
    tnum = int(re.findall(r'(\d+)', tnum)[0])
    if tnum != 1:
        for _ in range(tnum-1):
            locator = (By.XPATH, "//button[@id='next']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()

    locator = (By.XPATH, '//span[@id="numPages"]')
    tnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    tnum = int(re.findall(r'(\d+)', tnum)[0])
    try:
        locator = (By.XPATH, "//embed[@id='plugin'] | (//div[@class='textLayer'])[last()][string-length()>100]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        locator = (By.XPATH, "//embed[@id='plugin'] | (//div[@class='textLayer'])[last()-1][string-length()>100]")
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))

    before = len(driver.page_source)
    time.sleep(1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.5)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    divs = soup.find_all('div', class_="textLayer")
    div = ''
    for di in divs:div+=str(di)
    if (div == None) or (div == ''):div = soup.find('embed', id="plugin")
    div = BeautifulSoup(div, 'html.parser')
    driver.switch_to_default_content()
    return div



data = [
    ["gcjs_gqita_baojianxinxi_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/construct/getConstructInfoPage.do",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gglx':'报建信息'}),f2],

    ["gcjs_zhaobiao_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getBltPage.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getAnQuestionPage_project.do",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getEvaBulletinPage.do",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getwinBulletinPage_project.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_tongzhi_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getNoticePage.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'通知公告'}), f2],

    ["zfcg_zhaobiao_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/govermentPurchase/getMongoGovPurchaseNoticePage.do/1",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/govermentPurchase/getMongoGovPurchaseNoticePage.do/2",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/govermentPurchase/getMongoGovPurchaseNoticePage.do/4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta_large(conp,data=data,diqu="福建省厦门市",**args)
    est_html(conp,f=f3,**args)

# 更新日期:2019/7/9
if __name__=='__main__':
    # work(conp=["postgres","since2015","192.168.3.171","fujian","xiamen"])



    # for d in data[3:]:
    #     url = d[1]
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     d1 = f2(driver)
    #     print(d1)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     d2 = f1(driver, 1)
    #     print(d2.values)
    #     for i in d2[2].tolist():
    #         f = f3(driver, i)
    #         print(f)
    #
    driver = webdriver.Chrome()
    url='http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/agentBid.do?leftIndex=F005&uniqueId=O35020000004ca37468fee546a7a105354c88991d6a&objId=6ede2fd5-9370-426f-9eee-ec983e1f3a47'
    df = f3(driver, url)
    print(df)
