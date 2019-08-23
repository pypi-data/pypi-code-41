import json
import random
import re
from datetime import datetime

import math
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time



_name_ = 'hubei_dangyang_zfcg'


def f1(driver, num):
    driver.get(re.sub('page=\d+', 'page=' + str(num), driver.current_url))
    page = driver.page_source
    body = page.encode('latin-1').decode('unicode_escape')
    names = re.findall('\"title\":\"([^"]+)\"', body)
    vc_inputtime = re.findall('\"vc_inputtime\":\"([^"]+)\"', body)
    vc_department = re.findall('\"vc_department\":\"([^"]+)\"', body)
    index = re.findall('\"vc_number\":\"([^"]+)\"', body)
    n_id = re.findall('\"n_id\":\"([^"]+)\"', body)
    data = []
    for n, vi, vd, ind, id in zip(names, vc_inputtime, vc_department, index, n_id):

        href = 'http://xxgk.dangyang.gov.cn/show.html?aid=10&id=' + id
        info = json.dumps({"department": vd,"index":ind}, ensure_ascii=False)
        temp = [n, vi, href, info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    page = driver.page_source
    body = page.encode('latin-1').decode('unicode_escape')
    total_items = re.findall('allnums\":\"(\d+)', body)[0]
    total_page = math.ceil(int(total_items) / 20)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//td[@id="tableDiv"]')
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
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('td', id='tableDiv')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "https://xxgkapi.cn3x.com.cn/show/lists?jsoncallback=jQuery31109733300098252529_1565062723220&areaid=10&webid=352&cid=44&sid=&page=10&pagenums=20&orderby=0&_="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "https://xxgkapi.cn3x.com.cn/show/lists?jsoncallback=jQuery3110858988442880732_1565071713367&areaid=10&webid=352&cid=45&sid=&page=2&pagenums=20&orderby=0&_="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

# http://www.dangyang.gov.cn/ 湖北省当阳市人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省当阳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "hubei_dangyang_zfcg"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'https://xxgkapi.cn3x.com.cn/show/lists?jsoncallback=jQuery31109733300098252529_1565062723220&areaid=10&webid=352&cid=44&sid=&page=10&pagenums=20&orderby=0&_=1565062723223')
    # # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp)
