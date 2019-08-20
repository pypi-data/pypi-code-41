import json
import random
import re
from datetime import datetime

import math
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time



def f1(driver, num):

    locator = (By.XPATH, '//span[@class="pages"]/em[@class="curr_page"]')
    cnum = math.ceil(int(WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text)/12)
    locator = (By.XPATH, '//ul[@class="wp_article_list"]/li[1]/div/span/a')
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]

    if int(cnum) != int(num):
        new_url = re.sub('list[\d]*','list'+str(num),driver.current_url)
        driver.get(new_url)
        locator=(By.XPATH, '//ul[@class="wp_article_list"]/li[1]/div/span/a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []

    content_list = body.xpath('//ul[@class="wp_article_list"]/li')
    for con in content_list:
        name = con.xpath('./div/span/a/@title')[0].strip()
        url = 'http://zcc.sdau.edu.cn' + con.xpath('./div/span/a/@href')[0].strip()
        ggstart_time = con.xpath('./div[2]/span/text()')[0].strip()

        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    locator = (By.XPATH, '//span[@class="pages"]/em[@class="all_pages"]')
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(total_page)




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//td[@valign="top"][@class="content"][string-length()>50]')
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
    div = soup.find('td', attrs={'valign':"top",'class':''})

    if div == None:
        raise ValueError

    return div


data = [
    ["qycg_zhaobiao_gg",
     "http://zcc.sdau.edu.cn/932/list.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiao_gg",
     "http://zcc.sdau.edu.cn/934/list.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山东农业大学", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    # conp = ["postgres", "since2015", "192.168.3.171", "zlest", "zcc_sdau_edu_cn"]
    driver = webdriver.Chrome()

    f=f3(driver,'http://zcc.sdau.edu.cn/2015/0325/c932a10081/page.htm')
    print(f)

    # driver.get('http://zcc.sdau.edu.cn/932/list.htm')
    # f2(driver)
    # f1(driver, 3)
    # f1(driver, 5)
    # work(conp, )
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
