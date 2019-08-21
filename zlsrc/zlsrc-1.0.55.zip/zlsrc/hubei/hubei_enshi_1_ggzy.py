import json
import math

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html, add_info



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@width="887"]')
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
    div = soup.find('table', width="887")

    return div


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/div/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-60:]
    locator = (By.XPATH, '//td[@class="yahei redfont"]')
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    if int(cnum) != int(num):
        url = re.sub('Paging=\d+','Paging='+str(num),driver.current_url)
        driver.get(url)

        locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="ewb-info-items"]/li')
    for content in content_list:
        name = content.xpath("./div/a/@title")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = 'http://58.52.192.225' + content.xpath("./div/a/@href")[0].strip()
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//td[@class="huifont"]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)',txt)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["gcjs_zhaobiao_gg",
     "http://58.52.192.225/TPFront/jyxx/070001/070001001/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_biangeng_gg",
     "http://58.52.192.225/TPFront/jyxx/070001/070001002/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiao_gg",
     "http://58.52.192.225/TPFront/jyxx/070001/070001003/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_gqita_liu_jg_gg",
     "http://58.52.192.225/TPFront/jyxx/070001/070001004/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_gg",
     "http://58.52.192.225/TPFront/jyxx/070002/070002001/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_biangeng_gg",
     "http://58.52.192.225/TPFront/jyxx/070002/070002002/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_gg",
     "http://58.52.192.225/TPFront/jyxx/070002/070002003/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_liu_jg_gg",
     "http://58.52.192.225/TPFront/jyxx/070002/070002004/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="湖北省恩施州", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    # for d in data:
    #
    #     driver = webdriver.Chrome()
    #     url = d[1]
    #     driver.get(url)
    #     df = f1(driver, 2)
    #     #
    #     for u in df.values.tolist()[:4]:
    #         print(f3(driver, u[2]))
    #     driver.get(url)
    #
    #     print(f2(driver))
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "enshizhou"])
