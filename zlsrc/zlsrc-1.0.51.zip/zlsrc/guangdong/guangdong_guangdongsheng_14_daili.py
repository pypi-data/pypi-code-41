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
from zlsrc.util.fake_useragent import UserAgent

from zlsrc.util.etl import est_html, est_meta, add_info
import time

ua = UserAgent()

def get_response(url):
    driver_info = webdriver.DesiredCapabilities.CHROME

    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxy = {proxy_ip[0]: proxy_ip[1]}

        else:
            proxy={}
    except:
        proxy={}
    headers = {
        'User-Agent': ua.random,
    }
    page = requests.get(url, headers=headers, timeout=50, proxies=proxy)
    if page.status_code != 200:
        raise ConnectionError("response status code is %s"%page.status_code)

    return page.text

def f1(driver, num):

    new_url = re.sub('pageNo=\d+','pageNo='+str(num),driver.current_url)
    page = get_response(new_url)

    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='list']/li")
    data = []
    for content in content_list:
        try:
            name = content.xpath("./a/text()")[0].strip()
        except:name = '-'
        code = content.xpath("./span/text()")[0].strip()
        info_temp = {'code': code}
        try:
            ggstart_time = re.findall('\d{4}-\d{2}-\d{2}',code)[0]
        except:
            ggstart_time = '-'
            info_temp.update({"info":'网站无时间。'})
        url = 'http://www.gztpc.com' + content.xpath("./a/@href")[0].strip()


        info = json.dumps(info_temp,ensure_ascii=False)

        temp = [name, ggstart_time, url,info]
        # print(temp)
        data.append(temp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):

    locator = (By.XPATH, "//span[@class='Page_PageCount'][1]")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    driver.quit()
    return int(total_page)


def f3(driver, url):
    page = get_response(url)
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='maincontent')
    if div ==None:
        raise ValueError("div is None")

    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.gztpc.com/tender/list?pid=4028e68133f22e130133f2a837750000&pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_biangeng_gg",
     "http://www.gztpc.com/tender/list?pid=4028e68133f22e130133f2a893490001&pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiaohx_gg",
     "http://www.gztpc.com/tender/list?pid=4028e68133f22e130133f2aa297a0002&pageNo=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"单一来源"}), f2],

    ["jqita_zhongbiao_gg",
     "http://www.gztpc.com/tender/list?pid=4028e68133f22e130133f2aa5a780003&pageNo=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"成交"}), f2],

]

##广东广招招标采购有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_gztpc_com"]
    # work(conp,num=1,ipNum=0,headless=False)


    driver=webdriver.Chrome()
    f=f3(driver,"http://www.gztpc.com/tender/show?id=f47e4e884e27f39b01549f4bca1b1391")
    print(f)

    # driver = webdriver.Chrome()
    # driver.get('http://www.gztpc.com/tender/list?pid=4028e68133f22e130133f2a837750000&pageNo=1')
    # f1(driver,32)
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     df_list = f1(driver, i).values.tolist()
    #     print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
