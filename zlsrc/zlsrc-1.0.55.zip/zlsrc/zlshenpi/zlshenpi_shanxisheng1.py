import math
import os

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlsrc.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json


def f1(driver, num):
    url = driver.current_url
    if '/tzxmweb/pages/exception/images/404.png' in str(driver.page_source):
        locator = (By.XPATH, "//a[contains(string(), '返回首页')]")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).click()

    if 'pages/home/approvalResult/recordquery.jsp' in url:
        locator = (By.XPATH, '//table[@class="index-table"]/tbody/tr[child::td]/td[2]/a')
        val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text[-24:]
    else:
        locator = (By.XPATH, '//table[@class="index-table"]/tbody/tr[child::td][1]/td')
        val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text[-24:]
    locator = (By.XPATH, "//a[@class='cur']")
    cnum = int(WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text)

    if num != int(cnum):
        locator = (By.XPATH, "//input[@id='pageNum']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, "//input[@id='pageNum']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num)
        locator = (By.XPATH, "//div[@class='pageTurnTo']/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        if 'pages/home/approvalResult/recordquery.jsp' in url:
            locator = (By.XPATH,
                """//table[@class="index-table"]/tbody/tr[child::td]/td[2]/a[not(contains(string(), "%s"))]""" % val)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
        else:
            locator = (
            By.XPATH, """//table[@class="index-table"]/tbody/tr[child::td][1]/td[not(contains(string(), "%s"))]""" % val)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath('//table[@class="index-table"]/tbody/tr[child::td]')

    data = []
    for content in contents:
        if 'queryExamineAll' in driver.current_url:
            name, xm_code = content.xpath("./td[1]/text()|./td[1]/a/text()")

            href_tmp = content.xpath('./td[1]/a')
            if href_tmp != []:
                href = href_tmp[0].xpath('./@onclick')[0].strip()
            else:
                href = "-"
            shixiang = content.xpath('./td[2]/@title')[0].strip()
            shenpi_bumen = content.xpath('./td[3]/text()')[0].strip()
            result = content.xpath('./td[4]/a/text()|./td[4]/text()')[0].strip()
            piwenhao = content.xpath('./td[5]/@title')[0].strip()
            ggstart_time = content.xpath('./td[6]/text()')[0].strip()
            info_tmp = {"shixiang": shixiang, 'shenpi_bumen': shenpi_bumen, "xm_code": xm_code, "result": result,
                        "piwenhao": piwenhao}
        else:
            try:
                xm_code = content.xpath('./td[1]/text()')[0].strip()
            except:
                xm_code = '-'
            name = content.xpath('./td[2]/a/@title')[0].strip()
            company = content.xpath('./td[3]/text()')[0].strip()
            ggstart_time = content.xpath('./td[4]/text()')[0].strip()
            shenhe_status = content.xpath('./td[5]/text()')[0].strip()
            try:
                href = content.xpath('./td[2]/a/@onclick')[0].strip()
            except:
                href = "-"
            info_tmp = {"company": company, 'shenhe_status': shenhe_status, "xm_code": xm_code}
        if href == '-':
            info_tmp.update({'hreftype': '不可抓网页'})
        info = json.dumps(info_tmp, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)

    df = pd.DataFrame(data)
    return df


def f2(driver):
    if '/tzxmweb/pages/exception/images/404.png' in str(driver.page_source):
        locator = (By.XPATH, "//a[contains(string(), '返回首页')]")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).click()

    locator = (By.XPATH, "//div[@class='pageNum']/span[1]/strong")
    total_page = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text)
    driver.quit()
    return total_page


def f3(driver, url):
    o_url = 'http://www.shanxitzxm.gov.cn/tzxmweb/pages/home/approvalResult/recordquery.jsp'
    # if driver.current_url != o_url:
    driver.get(o_url)
    driver.execute_script(url)
    locator = (By.XPATH, '//div[@class="layui-layer-content"] | //div[@class="ucc-info-div"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    try:
        element = driver.find_element_by_xpath("//a[@class='layui-layer-ico layui-layer-close layui-layer-close1']")
        driver.execute_script("arguments[0].click()", element)
    except:
        pass
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_="layui-layer-content")
    if div == None:
        div = soup.find('div', class_="ucc-info-div")

    return div


data = [
    ["xm_shenpi_gg",
     "http://www.shanxitzxm.gov.cn/portalopenPublicInformation.do?method=queryExamineAll",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["xm_beian_gg",
     "http://www.shanxitzxm.gov.cn/tzxmweb/pages/home/approvalResult/recordquery.jsp",
     ["name", "ggstart_time", "href", "info"], f1,f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data,diqu="山西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "shanxisheng1"],num=1,headless=False)

    # for d in data[1:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
