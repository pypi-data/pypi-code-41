import pandas as pd
import re

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
    locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = re.findall('pageing=(\d+)',url)[0]
    if num != cnum:
        url=re.sub('(?<=pageing=)\d+',str(num),url)
        val = driver.find_element_by_xpath('//ul[@class="ewb-info-items"]/li[1]/a').get_attribute('href')

        driver.get(url)
        locator = (By.XPATH, "//ul[@class='ewb-info-items']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    ul = soup.find("ul", class_='ewb-info-items')

    lis = ul.find_all("li")

    data = []

    for li in lis:
        a = li.find("a")
        ggstart_time = li.find("span").get_text(strip=True)
        tmp = [a['title'], ggstart_time, "http://www.xxggzyjyw.com" + a["href"]]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    try:
        locator = (By.XPATH, '//ul[@class="ewb-page-items clearfix"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        total=driver.find_element_by_xpath('//ul[@class="ewb-page-items clearfix"]/li[last()-3]').text

        total = re.findall("\/(\d+)", total)[0]
        total = int(total)
    except:
        total = 1
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="mainContent"][string-length()>100]')

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

    div = soup.find('div', class_='article-block')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.xxggzyjyw.com/XIXIANTPFront/jyxx/003001/003001001/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://www.xxggzyjyw.com/XIXIANTPFront/jyxx/003001/003001002/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.xxggzyjyw.com/XIXIANTPFront/jyxx/003001/003001003/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.xxggzyjyw.com/XIXIANTPFront/jyxx/003002/003002001/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://www.xxggzyjyw.com/XIXIANTPFront/jyxx/003002/003002002/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.xxggzyjyw.com/XIXIANTPFront/jyxx/003002/003002003/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg", "http://www.xxggzyjyw.com/XIXIANTPFront/jyxx/003006/003006001/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],



]

##息县公共资源交易网
def work(conp, **args):
    est_meta(conp, data=data, diqu="河南省信阳市息县", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "henan", "xinyang"], num=1, total=2, html_total=10,
         pageloadtimeout=60)