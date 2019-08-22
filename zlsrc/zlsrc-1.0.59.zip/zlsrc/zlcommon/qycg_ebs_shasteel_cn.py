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

_name_ = 'qycg_ebs_shasteel_cn'


def f1(driver, num):
    page = int(num) * 10 - 9
    driver.get(re.sub('from=\d+', 'from=' + str(page), driver.current_url))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='form1']/table/tbody/tr[child::td]")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//form[@id='form1']/table/tbody/tr[child::td]")
    data = []
    info_temp = {}
    for content in content_list:
        name = content.xpath('./td[1]/a/text()')[0].strip()
        caigouzuzhi = content.xpath('./td[2]/text()')
        goods_name = content.xpath('./td[3]/text()')
        if caigouzuzhi:
            caigouzuzhi = caigouzuzhi[0].strip()
            info_temp.update({'caigouzuzhi': caigouzuzhi})
        if goods_name:
            goods_name = goods_name[0].strip()
            info_temp.update({'goods_name': goods_name})
        href = 'https://ebs.shasteel.cn/ieps/' + re.findall("\'([^\']+)\'", content.xpath('./td/a/@onclick')[0].strip())[0]
        ggstart_time = content.xpath('./td[4]/text()')[0].strip().replace('.', '-')
        info = json.dumps(info_temp, ensure_ascii=False)
        temp = [name, ggstart_time, href, info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    total_temp = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='flip']"))).text

    total_page = re.findall('共(\d+)页', total_temp)[0]

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//form[contains(@id,"CMZC000")][string-length()>50]')
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
    div = soup.find('form', sttrs={'id': re.compile('CMZC\d+')})
    return div


data = [
    ["qycg_zhaobiao_gg",
     "https://ebs.shasteel.cn/pur_portal/portal2/mana/view_nodes.jsp?catalogId=default&nodeId=82&from=11&total=32630",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_gg",
     "https://ebs.shasteel.cn/pur_portal/portal2/mana/view_nodes.jsp?catalogId=default&nodeId=1731&from=21&total=20568",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


# 江苏沙钢集团
def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏沙钢集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qycg_ebs_shasteel_cn"]
    # driver = webdriver.Chrome()
    # driver.get(data[0][1])
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp, total=50, ipNum=5, num=4)
