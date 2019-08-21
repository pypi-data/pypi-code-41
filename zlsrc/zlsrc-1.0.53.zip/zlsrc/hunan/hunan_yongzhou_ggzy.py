import pandas as pd
import re

from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_meta, est_html, add_info



def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[1]/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-50:]

    if "m-pagination-page" in driver.page_source:
        locator = (By.XPATH, '//li[@class="active"]/a')
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    else:
        cnum = 1
    if int(num) != int(cnum):
        new_url = re.sub('[about\-trade\d]*\.html', str(num) + '.html', driver.current_url)[0]
        driver.get(new_url)

        locator = (By.XPATH, "//ul[@class='wb-data-item']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath("//ul[@class='wb-data-item']/li")
    data = []
    for content in contents:
        name = content.xpath("./a/@title")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        href = 'http://ggzy.yzcity.gov.cn' + content.xpath('./a/@href')[0].strip()
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    if "m-pagination-page" in driver.page_source:
        locator = (By.XPATH, '//ul[@class="m-pagination-page"]/li[last()]')
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    else:
        total = 1
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='ewb-article'][string-length()>60]")

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

    div = soup.find('div', class_='ewb-article')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_zhaobiao_sigong_gg", "http://ggzy.yzcity.gov.cn/jyxx/003001/003001001/003001001001/about-trade.html",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"gctype": "房屋市政"}), f2],

    ["gcjs_zhaobiao_jianli_gg", "http://ggzy.yzcity.gov.cn/jyxx/003001/003001001/003001001002/about-trade.html",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"gctype": "交通"}), f2],

    ["gcjs_zhaobiao_kancha_gg", "http://ggzy.yzcity.gov.cn/jyxx/003001/003001001/003001001003/about-trade.html",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"gctype": "水利"}), f2],

    ["gcjs_gqita_gg", "http://ggzy.yzcity.gov.cn/jyxx/003001/003001001/003001001004/about-trade.html",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"gctype": "其他"}), f2],

    ["gcjs_biangeng_gg", "http://ggzy.yzcity.gov.cn/jyxx/003001/003001002/about-trade.html",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ###工程建设-中标
    ["gcjs_zhongbiao_gg", "http://ggzy.yzcity.gov.cn/jyxx/003001/003001003/about-trade.html",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ###政府采购-招标
    ["zfcg_zhaobiao_gc_gg", "http://ggzy.yzcity.gov.cn/jyxx/003002/003002001/003002001001/about-trade.html",
     ["name", "href", "ggstart_time", "info"],add_info(f1, {"jytype": "公开"}), f2],

    ["zfcg_zhaobiao_tanpan_gg", "http://ggzy.yzcity.gov.cn/jyxx/003002/003002001/003002001002/about-trade.html",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"jytype": "谈判"}), f2],

    ["zfcg_zhaobiao_cuoshang_gg", "http://ggzy.yzcity.gov.cn/jyxx/003002/003002001/003002001003/about-trade.html",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"jytype": "磋商"}), f2],

    ["zfcg_zhaobiao_xunjia_gg", "http://ggzy.yzcity.gov.cn/jyxx/003002/003002001/003002001004/about-trade.html",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"jytype": "询价"}), f2],

    ["zfcg_dyly_gg", "http://ggzy.yzcity.gov.cn/jyxx/003002/003002001/003002001005/about-trade.html",
     ["name", "href", "ggstart_time", "info"], f1, f2],


    ###政府采购-中标
    ["zfcg_zhongbiao_gg", "http://ggzy.yzcity.gov.cn/jyxx/003002/003002003/about-trade.html", ["name", "href", "ggstart_time", "info"],
     f1, f2],

    ["zfcg_gqita_gg", "http://ggzy.yzcity.gov.cn/jyxx/003002/003002004/about-trade.html",
     ["name", "href", "ggstart_time", "info"], f1, f2],


    ###政府采购-biangen
    ["zfcg_biangeng_gg", "http://ggzy.yzcity.gov.cn/jyxx/003002/003002002/about-trade.html", ["name", "href", "ggstart_time", "info"],
     f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省永州市", **args)

    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "hunan", "yongzhou"], num=3)
    # driver = webdriver.Chrome()
    for i in data[-4:]:
        driver= webdriver.Chrome()
        driver.get(i[1])
        df_list = f1(driver,1).values.tolist()
        for k in df_list[:2]:
            print(f3(driver, k[2]))
        driver.get(i[1])
        print(f2(driver))