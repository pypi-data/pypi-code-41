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



def f1(driver, num):
    new_url = re.sub('&page=\d+', '&page=' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, '//body[string-length()>200]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    page = driver.page_source

    body = BeautifulSoup(page, 'html.parser').text
    content_list = json.loads(body).get('docs')

    data = []
    for c in content_list:

        name = c.get('title')

        url = c.get('url')

        ggstart_time = c.get('time')

        temp = [name, ggstart_time, url]

        if '文章标题' not in temp:
            data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    page = driver.page_source
    body = BeautifulSoup(page, 'html.parser').text
    # print(page)
    total = int(json.loads(body).get('count'))
    total_page = math.ceil(total/20)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="xl_column"]')
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
    div = soup.find('div', class_='xl_column')
    return div


data = [
    ["gcjs_gqita_zhao_zhong_gg",
     "http://www.fjic.gov.cn/was5/web/search?channelid=244979&sortfield=-docreltime&classsql=chnlid%3D15908&prepage=20&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

#福建省经济信息中心
def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_fjic_gov_cn"]
    # driver = webdriver.Chrome()
    #
    # driver.get('http://www.fjic.gov.cn/was5/web/search?channelid=244979&sortfield=-docreltime&classsql=chnlid%3D15908&prepage=20&page=8')
    # print(f2(driver))
    # f1(driver, 1)
    # f1(driver, 5)
    work(conp, num=1,cdc_total=1,headless=False)
    # print(f3(driver, 'http://ztbzx.hbsjtt.gov.cn/Site/details_news.aspx?NewsGuid=I1300000001057866001002&type=gg'))
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     for i in range(1,i):
    #         df_list = f1(driver, i).values.tolist()
        #     print(df_list[:10])
        #     df1 = random.choice(df_list)
        #     print(str(f3(driver, df1[2]))[:100])
        #     driver.quit()
