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
    driver.get(re.sub('pageNumber=\d+', 'pageNumber=' + str(num), driver.current_url))
    locator = (By.XPATH, '//body/pre[string-length()>30]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = BeautifulSoup(page, 'html.parser').text
    content_list = json.loads(json.loads(body).get('data')).get('rows')

    data = []

    for c in content_list:
        name = c.get('noticeName')

        url = 'http://www.gzebid.cn/web-detail/frontDetail?articleId=' + c.get('id')

        ggstart_time = c.get('publishTime')
        if ggstart_time is None or name =='': ggstart_time = 'None'
        if name is None or name == '':name = "None"
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//body/pre[string-length()>30]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = BeautifulSoup(page, 'html.parser').text
    total = json.loads(body)
    total_page = int(json.loads(total.get('data')).get('total') / 15)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="xl_column"]|//table[contains(@class,"table")]')
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
    if div is None:
        div = soup.find('table', {'class':re.compile('table')})
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.gzebid.cn/web-list/articles?categoryId=b66478f0930d4162be8df579268b39a7&pageNumber=1&pageSize=15&title=&pushTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiao_1_gg",
     "http://www.gzebid.cn/web-list/articles?categoryId=ead7af9fccec46aaa91797fc218dcdd0&pageNumber=1&pageSize=15&title=&pushTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_qita_gg",
     "http://www.gzebid.cn/web-list/articles?categoryId=67ece36282d0465f8352283f34bc9123&pageNumber=1&pageSize=15&title=&pushTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_biangeng_gg",
     "http://www.gzebid.cn/web-list/articles?categoryId=3aa62ebb9ad948899521b7c0466f789c&pageNumber=1&pageSize=15&title=&pushTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiaohx_gg",
     "http://www.gzebid.cn/web-list/articles?categoryId=83d3368a846745c09536b77227a3d76f&pageNumber=1&pageSize=15&title=&pushTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiao_gg",
     "http://www.gzebid.cn/web-list/articles?categoryId=833749ccca314d05a9ca19440c63af48&pageNumber=1&pageSize=15&title=&pushTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_qita_2_gg",
     "http://www.gzebid.cn/web-list/articles?categoryId=ff2962347e664004afabab75d7787731&pageNumber=1&pageSize=15&title=&pushTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

#广咨电子招投标交易平台
def work(conp, **args):
    est_meta(conp, data=data, diqu="广咨电子招投标交易平台", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_gzebid_com"]
    # driver = webdriver.Chrome()

    # driver.get('http://www.hbeba.com/Client/liebiao/List.aspx?flag=Tender')
    # print(f2(driver))
    # f1(driver, 1)
    # f1(driver, 5)
    work(conp, ipNum=2,num=1)
    # print(f3(driver, 'http://www.gzebid.cn/web-detail/frontDetail?articleId=1297f9ef2c8b4d158ead2eca1bf44124'))
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i = random.randint(1, total)
    #     driver.get(d[1])
    #     print(d[1])
    #     for i in range(1, i,10):
    #         df_list = f1(driver, i).values.tolist()
    #         print(df_list[:3])
    #
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
