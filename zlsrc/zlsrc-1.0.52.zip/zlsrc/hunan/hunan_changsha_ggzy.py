import json
import math
import re

import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time



def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="list-ul"]/li[1]/p/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-10:]

    locator = (By.XPATH, '//ul[@class="pages-list"]/li[1]/a')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)\/',txt)[0]
    if int(cnum) != num:
        new_u = re.sub('index[_\d]*','index_'+str(num),driver.page_source)
        driver.get(new_u)
        locator = (By.XPATH, '//ul[@class="list-ul"]/li[1]/p/a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data_temp=[]
    body = etree.HTML(driver.page_source)
    content_list = body.xpath('//ul[@class="list-ul"]/li')
    for content in content_list:
        name = content.xpath("./p/a/@title")[0].strip()
        href = "https://fwpt.csggzy.cn" + content.xpath("./p/a/@href")[0].strip()
        ggstart_time = content.xpath("./p[2]/text()")[0]
        temp = [name, ggstart_time, href]
        data_temp.append(temp)

    df = pd.DataFrame(data=data_temp)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="pages-list"]/li[1]/a')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)',txt)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="contentdiv"]')
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
    div = soup.find('div', class_='contentdiv')

    return div


data = [
    #  房建市政
    ["gcjs_zhaobiao_fjsz_gg",
     "https://fwpt.csggzy.cn/jyxxfjzbgg/index.jhtml",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'房建市政'}), f2],

    ["gcjs_gqita_cheng_bu_fjsz_gg",
     "https://fwpt.csggzy.cn/jyxxfjcqdy/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'房建市政',"Tag2":"澄清补充"}), f2],

    ["gcjs_zhongbiaohx_fjsz_gg",
     "https://fwpt.csggzy.cn/jyxxfjzbgs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'房建市政'}), f2],

    ["gcjs_gqita_fjsz_gg",
     "https://fwpt.csggzy.cn/jyxxfjqtgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'房建市政'}), f2],


     # 交通工程
    ["gcjs_zhaobiao_jiaotong_gg",
     "https://fwpt.csggzy.cn/jyxxjtzbgg/index.jhtml",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'交通工程'}), f2],

    ["gcjs_gqita_cheng_bu_jiaotong_gg",
     "https://fwpt.csggzy.cn/jyxxjtcqdy/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'交通工程',"Tag2":"澄清补充"}), f2],

    ["gcjs_zhongbiaohx_jiaotong_gg",
     "https://fwpt.csggzy.cn/jyxxjtzbgs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'交通工程'}), f2],

    ["gcjs_gqita_jiaotong_gg",
     "https://fwpt.csggzy.cn/jyxxjtqtgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'交通工程'}), f2],

    # 水利工程
    ["gcjs_zhaobiao_shuili_gg",
     "https://fwpt.csggzy.cn/jyxxslzbgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_gqita_cheng_bu_shuili_gg",
     "https://fwpt.csggzy.cn/jyxxslcqdy/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程',"Tag2":"澄清补充"}), f2],

    ["gcjs_zhongbiaohx_shuili_gg",
     "https://fwpt.csggzy.cn/jyxxslzbgs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_gqita_shuili_gg",
     "https://fwpt.csggzy.cn/jyxxslqtgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    # 政府采购
    ["zfcg_zhaobiao_gg",
     "https://fwpt.csggzy.cn/jyxxzczbgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '政府采购'}), f2],
    ["zfcg_biangeng_gg",
     "https://fwpt.csggzy.cn/jyxxzcgzgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '政府采购'}), f2],

    ["zfcg_zhongbiao_gg",
     "https://fwpt.csggzy.cn/jyxxzczbgs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '政府采购'}), f2],

    ["zfcg_gqita_gg",
     "https://fwpt.csggzy.cn/jyxxzcqtgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '政府采购'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省长沙市", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':


    conp = ["postgres", "since2015", "192.168.3.171", "hunan", "changsha"]
    # work(conp,num=3)
    for i in data:
        driver = webdriver.Chrome()
        driver.get(i[1])
        df = f1(driver,1)
        for k in df.values.tolist()[:3]:
            print(f3(driver,k[2]))
        driver.get(i[1])

        print(f2(driver))
    #     driver = webdriver.Chrome()

    # driver.get("https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1&add=PUBLICITY")
    # print(f2(driver))
    # f1(driver, 3)




