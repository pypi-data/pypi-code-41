import json
import random

import math
import re

import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time
from datetime import datetime,timedelta


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="detail clearfloat"]/ul/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="detail clearfloat"]/ul/li/div/a').get_attribute("href")[-50:]
    cnum = driver.find_element_by_xpath('//a[@class="cur-ye"]/span').text
    if int(cnum) != int(num):
        driver.execute_script('pagination(%s);' % num)
        locator = (By.XPATH, '''//div[@class="detail clearfloat"]/ul/li/div/a[not(contains(@href,"%s"))]''' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="detail clearfloat"]/ul/li')
    for content in content_list:
        info_temp = {}
        name = content.xpath("./div[1]/a/text()")[0].strip()
        url = "https://etp.faw.cn" + content.xpath("./div[1]/a/@href")[0].strip()
        if 'gg/ggList' not in driver.current_url:
            ggstart_time = content.xpath("./div[2]/span[2]/text()")[0].split('：')[1].strip()
        else:
            ggstart_time = content.xpath("./div[2]/span[2]/span/text()")[0].strip()
        gg_type = re.sub('\s','',content.xpath("./div[2]/span[1]/text()")[0])
        project_type = re.sub(r'\s+','',content.xpath("./div[3]/span[1]/text()")[0].strip())

        try:
            # deadline = content.xpath("./div[1]/span")[0].xpath('string(.)')
            days = content.xpath("./div[1]/span/font[1]/text()")[0].strip()
            hours = content.xpath("./div[1]/span/font[2]/text()")[0].strip()
            minutes = content.xpath("./div[1]/span/font[3]/text()")[0].strip()
            seconds = content.xpath("./div[1]/span/font[4]/text()")[0].strip()
            deadline = datetime.strptime(ggstart_time,'%Y-%m-%d') + timedelta(days=int(days)) + timedelta(hours=int(hours)) + timedelta(minutes=int(minutes))+ timedelta(seconds=int(seconds))

        except:
            deadline = content.xpath("./div[1]/span")[0].xpath('string(.)')

        info_temp.update({'deadline': str(deadline),'gg_type': gg_type,'project_type': project_type})

        # print(name,url,ggstart_time,deadline,project_type)
        info = json.dumps(info_temp,ensure_ascii=False)
        temp = [name, ggstart_time, url, info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    driver.maximize_window()
    locator = (By.XPATH, '//div[@class="page-container"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//div[@class="page-container"]/a[last()-1]/span').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="detail"]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    if 'iframepage' in driver.page_source:
        iframe = driver.find_element_by_xpath('//iframe[@id="iframepage"]')
        if iframe:
            driver.switch_to.frame(iframe)
            page1 = driver.page_source
            soup1 = BeautifulSoup(page1, 'html.parser')
            div1 = soup1.find('body')
            driver.switch_to_default_content()
        else:div1 =''

    else:div1 =''

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
    div = soup.find('div', class_='detail')
    return str(div)+ str(div1)


data = [
    ["qycg_zhaobiao_gg",
     "https://etp.faw.cn/gg/ggList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qycg_biangeng_gg",
     "https://etp.faw.cn/gg/bgggList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qycg_zhongbiaohx_gg",
     "https://etp.faw.cn/gg/zbhxrList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],

    ["qycg_zhongbiao_gg",
     "https://etp.faw.cn/gg/zbjgList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qycg_zsjg_gg",
     "https://etp.faw.cn/gg/zgscList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],
    #
    ["qycg_zhaobiao_fzb_gg",
     "https://etp.faw.cn/gg/toXinXiList?gongGaoType=5&xmLeiXing=&ggStartTimeEnd=&hangYeType=5",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'tag':'非招标'}), f2],
    ["qycg_biangeng_fzb_gg",
     "https://etp.faw.cn/gg/toXinXiList?gongGaoType=6&xmLeiXing=&ggStartTimeEnd=&hangYeType=5",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'tag':'非招标'}), f2],
    ["qycg_zhongbiaohx_fzb_gg",
     "https://etp.faw.cn/gg/toXinXiList?gongGaoType=7&xmLeiXing=&ggStartTimeEnd=&hangYeType=5",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'tag':'非招标'}), f2],

    ["qycg_zhongbiao_fzb_gg",
     "https://etp.faw.cn/gg/toXinXiList?gongGaoType=15&xmLeiXing=&ggStartTimeEnd=&hangYeType=5",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'tag':'非招标'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国一汽电子招标采购平台", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    # conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "etp_fawiec_com"]
    # work(conp,num=5)
    # driver = webdriver.Chrome()
    for d in data:

        driver = webdriver.Chrome()
        driver.get(d[1])
        toal = f2(driver)
        driver = webdriver.Chrome()
        driver.get(d[1])
        print(d[1])
        for i in range(1,toal,5):
            df = f1(driver, i).values.tolist()

            ur = random.choice(df)
            print(ur)
            print(f3(driver, ur[2]))
            driver.get(d[1])
        driver.quit()


    # print(f3(driver, 'https://etp.faw.cn/gg/toXinXiDetail1?guid=9ea65972-da52-4f0f-be9e-8b41eaaee7f4&xxSource=1'))
# driver.close()