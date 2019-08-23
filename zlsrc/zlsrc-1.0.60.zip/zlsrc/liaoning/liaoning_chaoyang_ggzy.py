import re

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
    locator = (By.XPATH, "//td[@class='huifont']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_xpath("//td[@class='huifont']").text.split('/')[0])
    locator = (By.XPATH, "//tr[@height='22']/td[2]")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//tr[@height='22']/td[2]").text
    if int(cnum) != int(num):
        url = '='.join(driver.current_url.split("=")[:-1]) + "=" + str(num)
        driver.get(url)
        locator = (
            By.XPATH, '//tr[@height="22"]/td[2][not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.ID, 'List')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//tr[@height='22']")
    for content in content_list:
        name = content.xpath("./td[2]")[0].xpath("string(.)").strip()
        ggstart_time = content.xpath("./td[3]/font/text()")[0].strip()[1:-1]
        url = "http://ggzy.zgcy.gov.cn" + content.xpath("./td[2]/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//td[@class='huifont']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = int(driver.find_element_by_xpath("//td[@class='huifont']").text.split('/')[1])

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo']|//div[@class='news-article']")
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
    div = soup.find('div', id="tblInfo")
    if not div:
        div = soup.find('table', id="tblInfo")
        if not div:
            div = soup.find('div', class_="news-article")
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://ggzy.zgcy.gov.cn/cyfront/ShowInfo/JSGC.aspx?categoryNum=002002001&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.zgcy.gov.cn/cyfront/ShowInfo/JSGC.aspx?categoryNum=002002002&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://ggzy.zgcy.gov.cn/cyfront/ShowInfo/JSGC.aspx?categoryNum=002002003&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://ggzy.zgcy.gov.cn/cyfront/ShowInfo/JSGC.aspx?categoryNum=002001001&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.zgcy.gov.cn/cyfront/ShowInfo/JSGC.aspx?categoryNum=002001002&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzy.zgcy.gov.cn/cyfront/ShowInfo/JSGC.aspx?categoryNum=002001003&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="辽宁省朝阳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    # work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "chaoyang"])
    url = 'http://ggzy.zgcy.gov.cn/cyfront/infodetail?infoid=13ee640a-23e8-4b2d-a20f-6fe24469d5df'
    driver = webdriver.Chrome()
    print(f3(driver, url))
