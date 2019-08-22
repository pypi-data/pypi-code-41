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
from zlsrc.util.etl import  est_meta, est_html, add_info



def f1(driver, num):
    url = driver.current_url

    url = re.sub("[0-9]*.html", "%d.html" % num, url)
    # print(url)
    driver.get(url)

    locator = (By.XPATH, "//li[@class='pagelink current'][string()='%d']" % num)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//ul[@class='ewb-r-items']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("ul", class_="ewb-r-items")

    lis = ul.find_all("li")

    data = []
    for li in lis:
        a = li.find("a")
        span = li.find("span")
        ggstart_time = re.sub("[\[\]]", '', span.text.strip())
        tmp = [a["title"], "http://jyzx.yiyang.gov.cn" + a["href"], ggstart_time]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='ewb-r-items']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.CLASS_NAME, "wb-page-number")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_class_name("wb-page-number").text.split("/")[1]

    total = int(total)

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "ewb-info-bd")

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

    div = soup.find('div', class_='ewb-info-bd')

    return div


data = [
    ["gcjs_gqita_fangwushizheng_gg", "http://jyzx.yiyang.gov.cn/jyxx/003001/003001001/2.html", ["name", "href", "ggstart_time", "info"],
     add_info(f1, {"gctype": "房屋市建"}), f2],

    ["gcjs_gqita_shuili_gg", "http://jyzx.yiyang.gov.cn/jyxx/003001/003001002/2.html", ["name", "href", "ggstart_time", "info"],
     add_info(f1, {"gctype": "水利"}), f2],

    ["gcjs_gqita_jiaotong_gg", "http://jyzx.yiyang.gov.cn/jyxx/003001/003001003/2.html", ["name", "href", "ggstart_time", "info"],
     add_info(f1, {"gctype": "交通"}), f2],

    ["gcjs_gqita_gg", "http://jyzx.yiyang.gov.cn/jyxx/003001/003001004/2.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_gqita_gg", "http://jyzx.yiyang.gov.cn/jyxx/003002/003002001/2.html", ["name", "href", "ggstart_time", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省益阳市", **args)

    est_html(conp, f=f3, **args)

# work(conp=["postgres","since2015","127.0.0.1","hunan","yiyang"])
