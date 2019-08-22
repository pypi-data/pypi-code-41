import json
from math import ceil
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//pre[contains(string(), 'NoticeTitle')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall(r'pageIndex=([0-9]+)', url)[0]

    if num != int(cnum):
        locator = (By.XPATH, "//pre")
        txt1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        tj1 = json.loads(txt1)
        val1 = tj1['RESULT'][0]['NoticeID']
        url = re.sub('pageIndex=[0-9]+', 'pageIndex=%d' % num, url)
        driver.get(url)
        locator = (By.XPATH, "//pre[contains(string(), 'NoticeTitle')]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//pre")
        txt2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        tj2 = json.loads(txt2)
        val2 = tj2['RESULT'][0]['NoticeID']
        if val1 == val2:
            raise ValueError

    locator = (By.XPATH, "//pre")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    ul = json.loads(txt)
    lis = ul['RESULT']
    data = []
    dataType = re.findall(r'ggtype=(.*?)&', url)[0]
    for tr in lis:
        name = tr['NoticeTitle']
        ggstart_time = tr['PubTime']
        href = 'http://scs.inspur.com/GGDetail.htm?dataType='+dataType+'&id='+tr['NoticeID']
        xm_num = tr['RFQBillCode']
        xm_hy = tr['SysSubTypeName']
        kbstart_time = tr['OpenTime']
        tbend_time = tr['BidEndTime']
        info = {'xm_num':xm_num, 'xm_hy':xm_hy, 'kbstart_time':kbstart_time, 'tbend_time':tbend_time}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//pre[contains(string(), 'NoticeTitle')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//pre")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    txt_json = json.loads(txt)
    total = txt_json['TOTALCOUNT'][0]['TOTALCOUNT']
    num = ceil(int(total)/10)
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='ggNotes'][string-length()>200]")
    WebDriverWait(driver, 40).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.5)
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
    div = soup.find('div', class_='ggdetail-box mb50')
    return div


data = [

    ["qycg_zhaobiao_hw_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=0&ggtype=CRFQ&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["qycg_zhaobiao_xunjia_hw_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=0&ggtype=SRFQ&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhaobiao_tanpan_hw_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=0&ggtype=TPFQ&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiao_hw_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=0&ggtype=ZBGS&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #######

    ["qycg_zhaobiao_fw_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=2&ggtype=CRFQ&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["qycg_zhaobiao_xunjia_fw_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=2&ggtype=SRFQ&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhaobiao_tanpan_fw_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=2&ggtype=TPFQ&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiao_fw_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=2&ggtype=ZBGS&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #######
    ["qycg_zhaobiao_gc_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=1&ggtype=CRFQ&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["qycg_zhaobiao_xunjia_gc_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=1&ggtype=SRFQ&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiao_gc_gg",
     "http://scs.inspur.com/MetaPortlet/EPP/GGList/ConfigTools/CEPPWebHandler.ashx?projectType=1&ggtype=ZBGS&relTime=0&keyWord=&pageSort=desc&tagFlag=0&pageIndex=1&rowCount=10&isOpenOnly=True&canOpenDetal=True",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]



def work(conp, **args):
    est_meta(conp, data=data, diqu="浪潮集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "scs_inspur_com"])

    #
    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = d[-1](driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=d[-2](driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


