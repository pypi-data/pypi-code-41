import json
import re

import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta
import time


def f1(driver, num):


    cnum = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,"//li[@class='active']/a"))).text
    val = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,"//ul[@id='infolist']/li[1]/div/a"))).get_attribute('href')[-50:]
    if int(cnum) != int(num):
        new_url = re.sub('pageIndex=\d+', 'pageIndex=' + str(num), driver.current_url)
        driver.get(new_url)
        locator = (By.XPATH, '//ul[@id="infolist"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, '//ul[@id="infolist"]/li')))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@id="infolist"]/li')
    for content in content_list:
        info_temp = {}
        name = content.xpath("./div/a/@title")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        try:
            area = content.xpath('./div/a/font[1]/text()')[0].strip().strip('[]')
            info_temp.update({'area':area})
        except:
            pass
        try:
            zblx = content.xpath('./div/a/font[2]/text()')[0].strip().strip('[]')
            info_temp.update({'zblx':zblx})
        except:
            pass
        info = json.dumps(info_temp,ensure_ascii=False)
        url = "http://ggzy.jz.gov.cn" + content.xpath("./div/a/@href")[0].strip()
        temp = [name, ggstart_time, url,info]
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    total_text = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='m-pagination-info']"))).text
    total_temp = int(re.findall('\d+', total_text)[0])
    total_page = math.ceil(total_temp/15)

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    if "ewb-info-bd" in driver.page_source:
        locator = (By.CLASS_NAME, "ewb-info-bd")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = True
    elif "tblInfo" in driver.page_source:
        locator = (By.ID, "tblInfo")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = False
    else:
        locator = (By.ID, "news-article")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 3
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
    if flag == True:
        div = soup.find('div', class_="ewb-info-bd")
    elif flag == 3:
        div = soup.find('div', class_="news-article")
    else:
        div = soup.find("table", id="tblInfo")
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001002/001002001/moreinfojy.html?categoryNum=001002001&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001002/001002003/moreinfojy.html?categoryNum=001002003&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://ggzy.jz.gov.cn/jyxx/001002/001002002/moreinfojy.html?categoryNum=001002002&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001002/001002004/moreinfojy.html?categoryNum=001002004&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001001/001001001/moreinfojy.html?categoryNum=001001001&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.jz.gov.cn/jyxx/001001/001001002/moreinfojy.html?categoryNum=001001002&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001001/001001003/moreinfojy.html?categoryNum=001001003&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001001/001001004/moreinfojy.html?categoryNum=001001004&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001007/001007001/moreinfojy.html?categoryNum=001007001&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001007/001007003/moreinfojy.html?categoryNum=001007003&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_liubiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/001007/001007004/moreinfojy.html?categoryNum=001007004&pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="辽宁省锦州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "jinzhou"], ipNum=0)
    # url = "http://ggzy.jz.gov.cn/jyxx/077002/077002001/1.html"
    # driver = webdriver.Chrome()
    # driver.get(url)
    #
    # for i in range(1,118):f1(driver,i)
    # driver.quit()
