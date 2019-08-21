import json

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta_large
from zlsrc.util.etl import est_meta, est_html, add_info



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', class_='content')
    return div


def f1(driver, num):

    locator = (By.XPATH, '//ul[@class="article-list"]/li[1]/div/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-15:]

    locator = (By.XPATH, '//li[@class="selected"]')
    cnum = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text

    if int(cnum) != int(num):
        driver.execute_script("location.href='index_%s.jhtml';"%num)

        locator = (By.XPATH, '//ul[@class="article-list"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="article-list"]/li')
    for content in content_list:
        name = content.xpath("./div/a/text()")[0].strip()
        area = content.xpath("./div/a/label/text()")[0].strip()
        ggstart_time = content.xpath("./div/text()")[0].strip()
        url = content.xpath("./div/a/@href")[0].strip()
        info = json.dumps({'area':area},ensure_ascii=False)
        temp = [name, ggstart_time, url,info]
        data.append(temp)

    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="pages-list"]/li/a')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    total_page = re.findall('\/(\d+)',txt)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["gcjs_zhaobiao_gg",
     "http://www.bidding.hunan.gov.cn/jyxx/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"公告"}), f2],
    #
    ["gcjs_zhongbiaohx_gg",
     "http://www.bidding.hunan.gov.cn/jyxxzbhx/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"公示"}), f2],
    #
    ["gcjs_zhongbiao_gg",
     "http://www.bidding.hunan.gov.cn/jyxxzbjg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"公示"}), f2],
]


def work(conp, **arg):
    est_meta_large(conp, data=data, diqu="湖南省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    # url = "http://www.ahtba.org.cn/Notice/hunanNoticeSearch?spid=714&scid=597&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15"
    # for d in data:
    #
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver, 2)
    #     for ur in df.values.tolist():
    #         try:
    #             print(f3(driver, ur[2]))
    #         except:print(1111111,ur[2])
    #     driver.get(d[1])
    #     print(f2(driver))

    #
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "hunansheng"])
