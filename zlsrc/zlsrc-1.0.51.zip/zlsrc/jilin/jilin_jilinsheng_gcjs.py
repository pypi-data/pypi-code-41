import json
import random
import re

import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta
from zlsrc.util.fake_useragent import UserAgent
import time


def f1(driver, num):
    new_url = re.sub('pageNumber=\d+?', 'pageNumber=' + str(num), driver.current_url)
    driver.get(new_url)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    body = soup.text
    body_json = json.loads(body)
    content_list = body_json.get('rows')
    data = []
    for content in content_list:
        name = content.get("projectName")
        project_code = content.get("projectNum")
        project_type = content.get("dataType").get('text')
        project_area = content.get("region").get('text')
        ggstart_time = content.get("releaseDate")
        id = content.get("id")
        url_temp = driver.current_url.split('list')[0]

        url = url_temp  + ('detail/' if 'resultInfo' not in url_temp else 'todetail/') + str(id)
        info = json.dumps({"project_code": project_code, "project_type": project_type, 'project_area': project_area}, ensure_ascii=False)

        temp = [name, ggstart_time, url, info]
        data.append(temp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')
    body = soup.text
    body_json = json.loads(body)
    total_items = body_json['total']
    total_page = math.ceil(int(total_items) / 50)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='container']")
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
    soup = BeautifulSoup(page, 'html.parse')
    div = soup.find('div', class_='container')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.jlsjsxxw.com:20001/web/bblistdata?sortOrder=desc&pageSize=50&pageNumber=1&_=1551778523007",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://www.jlsjsxxw.com:20001/web/alterationShow/list?sortOrder=desc&pageSize=50&pageNumber=1&_=1562924757681",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.jlsjsxxw.com:20001/web/candidateShow/list?sortOrder=desc&pageSize=50&pageNumber=1&_=1551778629317",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.jlsjsxxw.com:20001/web/resultInfo/list?sortOrder=desc&pageSize=50&pageNumber=1&projectName=&dataType=&region=&_=1551778705090",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="吉林省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jilin"]
    # work(conp,ipNum=0,headless=False)
    # driver=webdriver.Chrome()
    # driver.get('http://www.jlsjsxxw.com:20001/web/bblistdata?sortOrder=desc&pageSize=10&pageNumber=1&_=1551778523007')
    # print(f2(driver))
    # for d in data[-1:]:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     for i in range(1, total, 10):
    #         driver.get(d[1])
    #         print(d[1])
    #         df_list = f1(driver, i).values.tolist()
    #         print(df_list[:10])
    #         df1 = random.choice(df_list)
    #         print(str(f3(driver, df1[2]))[:100])
    #
