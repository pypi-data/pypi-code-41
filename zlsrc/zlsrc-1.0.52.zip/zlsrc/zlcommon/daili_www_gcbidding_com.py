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
from zlsrc.util.etl import est_html, est_meta, add_info
import time




def f1(driver, num):

    locator = (By.XPATH, "//div[contains(@style,'block')]//ul[@class='pagination']/li[@class='active']/span")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, "//div[contains(@style,'block')]//ul[@class='newsList']/a[1]")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-15:]

    if int(cnum) != int(num):
        new_url = re.sub('page=\d+','page='+str(num),driver.current_url)
        driver.get(new_url)

        locator = (By.XPATH, '//div[@style="display: block;"]//ul[@class="newsList"]/a[1][not(contains(@href,"%s"))]'%(val))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[contains(@style,'block')]//ul[@class='newsList']/a")

    data = []
    for content in content_list:
        info_temp = {}
        name = content.xpath("./li/div[1]/text()")[0].strip()
        try:
            code = content.xpath("./li/div[2]/text()")[0].strip()
            info_temp.update({'code': code})
        except :
            pass
        ggstart_time = content.xpath("./li/div[3]/text()")[0].strip()

        url = 'https://www.gcbidding.com/' + content.xpath("./@href")[0].strip()


        info = json.dumps(info_temp,ensure_ascii=False)

        temp = [name, ggstart_time, url,info]
        data.append(temp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):

    locator = (By.XPATH, "//div[contains(@style,'block')]//ul[@class='pagination']/li[last()-1]/a")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//ul[@class='newsList']")
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
    div=soup.find('ul',class_='newsList')
    return div


data = [
    ["jqita_zhaobiao_gg",
     "https://www.gcbidding.com/portal/bidding/index?content=bidding-one&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_yucai_gg",
     "https://www.gcbidding.com/portal/bidding/index?content=bidding-two&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiaohx_gg",
     "https://www.gcbidding.com/portal/bidding/index?content=bidding-three&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"单一来源"}), f2],

    ["jqita_gqita_cheng_gg",
     "https://www.gcbidding.com/portal/bidding/index?content=bidding-four&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"澄清"}), f2],
    ["jqita_gqita_jieguo_gg",
     "https://www.gcbidding.com/portal/bidding/index?content=bidding-five&page=3",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"结果"}), f2],

]

##广东广招招标采购有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东广招招标采购有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_gcbidding_com"]
    work(conp)
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
