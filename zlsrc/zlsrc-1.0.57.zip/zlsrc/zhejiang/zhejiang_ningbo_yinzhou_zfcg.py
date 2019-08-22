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
from zlsrc.util.etl import est_html, est_meta
import time



def f1(driver, num):

    locator = (By.XPATH, '//span[@class="default_pgStartRecord"]')
    cnum = math.ceil(int(WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text)/12)
    locator = (By.XPATH, '//div[@class="default_pgContainer"]/table[1]/tbody/tr/td/a')
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]

    if int(cnum) != int(num):
        new_url = re.sub('pageNum=\d+','pageNum='+str(num),driver.current_url)
        driver.get(new_url)
        locator=(By.XPATH, '//div[@class="default_pgContainer"]/table[1]/tbody/tr/td/a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []

    content_list = body.xpath('//div[@class="default_pgContainer"]/table')
    for con in content_list:
        name = con.xpath('./tbody/tr/td/a/@title')[0].strip()
        url = 'http://nbyz.gov.cn' + con.xpath('./tbody/tr/td/a/@href')[0].strip()
        ggstart_time = con.xpath('./tbody/tr/td[3]/text()')[0].strip()

        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(total_page)




def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//table[@id="article"]')
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    except:
        if '无法访问此网站' in str(driver.page_source):
            return '无法访问此网站'
        else:raise ValueError
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
    div = soup.find('table', id='article')
    return div


data = [
    ["zfcg_gqita_zhao_zhong_he_gg",
     "http://nbyz.gov.cn/col/col106756/index.html?uid=250822&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhao_zhong_liu_gg",
     "http://nbyz.gov.cn/col/col107073/index.html?uid=250822&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省宁波市鄞州区", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_ningbo_yinzhou"]
    # driver = webdriver.Chrome()
    # driver.get('http://zfcg.qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401&0401')
    # f2(driver)
    # f1(driver, 3)
    work(conp, )
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     # for i in range(1,i):
    #     df_list = f1(driver, i).values.tolist()
    #     print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
