from math import ceil

import pandas as pd
import re

import requests
from zlsrc.util.fake_useragent import UserAgent
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import add_info, est_meta, est_html

start_url, pay = None, None


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    payloadData, noticeType = get_payloadData(pay, num)
    sesion = requests.session()
    res = sesion.post(url=start_url, headers=headers,proxies=proxies,timeout=40, data=json.dumps(payloadData))
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            html = json.loads(html)
            datalist = html["data"]['datalist']
            data = []
            for tr in datalist:
                if 'gcjs' in pay:
                    try:
                        tenderProjId = tr['tenderProjId']
                    except:
                        tenderProjId = ''
                    try:
                        proj_id = tr['proj_id']
                    except:
                        proj_id = ''
                    try:
                        pre_evaId = tr['pre_evaId']
                    except:
                        pre_evaId = ''
                    try:
                        evaId = tr['evaId']
                    except:
                        evaId = ''
                    try:
                        signUpType = tr['signUpType']
                    except:
                        signUpType = ''
                    try:
                        tenderProjCode = tr['tenderProjCode']
                    except:
                        tenderProjCode = ''
                    link = 'http://www.swsggzy.cn:82/hyweb/swebid/bidDetails.do?handle=1&tenderProjCode=' + tenderProjCode + '&noticeType=' + noticeType + '&flag=1&tenderProjId=' + tenderProjId + '&proj_id=' + proj_id + '&pre_evaId=' + pre_evaId + '&evaId=' + evaId + '&signUpType=' + signUpType
                    title = tr['noticeTitle']
                    try:
                        td = tr['sendTime']
                    except:
                        td = '-'
                    tmp = [title, td, link]
                    data.append(tmp)
                elif 'zfcg' in pay:
                    projId = tr['projId']
                    link = 'http://www.swsggzy.cn:82/hyweb/swebid/mongoGovBid.do?projId=' + projId + '&noticeType=' + noticeType
                    title = tr['noticeTitle']
                    try:
                        td = tr['publishTime']
                    except:
                        td = '-'
                    tmp = [title, td, link]
                    data.append(tmp)
            df = pd.DataFrame(data)
            df['info'] = None
            return df


def get_payloadData(pay, num):
    if pay == 'gcjs_zb':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'SWPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "A", 'transType': "",
                       'pubTime': "", 'state': "", 'noticeType': 1}
        noticeType = '1'
    elif pay == 'gcjs_bg':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'SWPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "A", 'transType': "",
                       'pubTime': "", 'state': "", 'noticeType': 2}
        noticeType = '2'
    elif pay == 'gcjs_zbhx':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'SWPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "A", 'transType': "",
                       'pubTime': "", 'state': "", 'noticeType': 3}
        noticeType = '3'
    elif pay == 'gcjs_zhb':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'SWPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "A", 'transType': "",
                       'pubTime': "", 'state': "", 'noticeType': 4}
        noticeType = '4'
    elif pay == 'zfcg_zb':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'SWPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "SWPT",
                       'transType': "", 'pubTime': "", 'state': "", 'noticeType': 1}
        noticeType = '1'
    elif pay == 'zfcg_zhb':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'SWPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "SWPT",
                       'transType': "", 'pubTime': "", 'state': "", 'noticeType': 2}
        noticeType = '2'
    elif pay == 'zfcg_bg':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'SWPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "SWPT",
                       'transType': "", 'pubTime': "", 'state': "", 'noticeType': 4}
        noticeType = '4'

    return payloadData, noticeType


def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}
    global start_url, pay
    start_url, pay = None, None
    url = driver.current_url
    start_url = url.rsplit('/', maxsplit=1)[0]
    pay = url.rsplit('/', maxsplit=1)[1]
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    payloadData, noticeType = get_payloadData(pay, 1)
    sesion = requests.session()
    res = sesion.post(url=start_url,proxies=proxies,timeout=40, headers=headers, data=json.dumps(payloadData))
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            html = json.loads(html)
            total = int(html["data"]['pagecount'])
            num_total = ceil(total/10)
            if num_total == 0: raise ConnectionError
            driver.quit()
            return int(num_total)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//div[@class='ggnr_con'][string-length()>300]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        txt = driver.find_element_by_xpath("//div[@class='ggnr_con']").text
        if '详见源网站' not in txt:
            locator = (By.XPATH, "//div[@class='ggnr_con'][string-length()>300]")
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
    div = soup.find('div', id="main")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.swsggzy.cn:82/hyweb/transInfo/getTenderInfoPage.do/gcjs_zb",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.swsggzy.cn:82/hyweb/transInfo/getTenderInfoPage.do/gcjs_bg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.swsggzy.cn:82/hyweb/transInfo/getTenderInfoPage.do/gcjs_zbhx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.swsggzy.cn:82/hyweb/transInfo/getTenderInfoPage.do/gcjs_zhb",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.swsggzy.cn:82/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/zfcg_zb",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.swsggzy.cn:82/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/zfcg_bg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.swsggzy.cn:82/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/zfcg_zhb",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省邵武市", **args)
    est_html(conp, f=f3, **args)

# 修改日期：2019/7/9
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "fujian", "shaowu"])

    # for d in data:
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
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://218.67.123.146:81/hyweb/wysebid/bidDetails.do?handle=1&tenderProjCode=E3507820125999930001&noticeType=1&flag=1&tenderProjId=A6A4D904-9E80-9E6D-1DEE-FF68CBEBA017&proj_id=2221&pre_evaId=&evaId=-1347&signUpType=0')
    # print(df)
