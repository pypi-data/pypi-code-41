import json
import random
import re
from datetime import datetime

import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time

_name_ = 'guangxi_guangxisheng_ggzy'



def f1(driver, num):
    # print(driver.current_url[driver.current_url.find('ggzyjy'):],'---------',re.sub('index[_\d]*',  'index_' + str((int(num)-1)) if int(num) != 1 else 'index', driver.current_url)[-30:],)
    driver.get(re.sub('index[_\d]*',  'index_' + str((int(num)-1)) if int(num) != 1 else 'index', driver.current_url))
    # print(driver.current_url)
    main_url = driver.current_url.rsplit('/',1)[0]
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='News-Content']/ul/li")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='News-Content']/ul/li")
    data = []
    for content in content_list:
        name = content.xpath('./span[last()]/a/text()|./span[last()]/a/font/text()')[0].strip()
        ggtype = content.xpath('./span[1]/a/text()')[0].strip()

        href = main_url + content.xpath('./span[last()]/a/@href')[0].strip(' .')
        ggstart_time = content.xpath('./div/text()')[0].strip()
        info = json.dumps({"comp":ggtype},ensure_ascii=False)
        temp = [name, ggstart_time, href,info]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    total_page = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='page mt20 clearfix']/a[last()-2]"))).text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="contentS"][string-length()>100]')
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
    div = soup.find('div', class_='contentS')
    return div


data = [
    ["gcjs_zhaobiao_gg","http://jtt.gxzf.gov.cn/zwgk/zfxxgk/ggzyjy/zbxx/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg","http://jtt.gxzf.gov.cn/zwgk/zfxxgk/ggzyjy/zbxx_217/index.html",["name", "ggstart_time", "href", "info"], f1, f2],


]

# 广西壮族公共资源交易
def work(conp, **args):
    '''
    容易封ip，ipNum 加满
    :param conp:
    :param args:
    :return:
    '''
    est_meta(conp, data=data, diqu="广西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "guangxi_guangxisheng_ggzy"]
    # driver = webdriver.Chrome()
    # driver.get(data[0][1])
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,num=1,ipNum=0,headless=False)
