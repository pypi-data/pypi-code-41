import json
import random
import re
import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from zlsrc.util.fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta
import time
from selenium import webdriver


def f1(driver, num):
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='list_left']/ul[1]/li[1]/a"))).get_attribute('href')[-20:]
    cnum = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='list']/div/select/option[@selected]"))).text
    cnum = re.findall('\d+', cnum)[0]
    if int(cnum) != int(num):
        new_url = re.sub('index[_\d]*', 'index_' + str(num), driver.current_url)

        driver.get(new_url)
        locator = (By.XPATH, "//div[@class='list_left']/ul[1]/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='list_left']/ul/li")
    # print(len(content_list))
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = 'http://www.hebeihongtai.cn' + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df

def f2(driver):
    href_temp = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//div[@class='list']/div/select/option[last()]"))).text
    #第19页
    total_page = re.findall('\d+',href_temp)[0]
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='neirong_n']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
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
    div = soup.find('div', class_="neirong_n")
    return div

data = [
    ["jqita_zhongbiao_gg",
     "http://www.hebeihongtai.cn/ztbgg/zhbgg/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg",
     "http://www.hebeihongtai.cn/ztbgg/zbgg/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]
# 河北鸿泰融新工程项目咨询股份有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "qycg_www_hebeihongtai_cn"]
    work(conp,num=1,cdc_total=15)

    # for d in data:
    #     # print(d[1])
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     for i in range(1,total,5):
    #         df = f1(driver,i)
    #         item_list = df.values.tolist()
    #         print(f3(driver, item_list[0][2]))
    #         driver.get(d[1])
    #     driver.quit()
    #
    # url = 'http://www.hebeihongtai.cn/ztbgg/zhbgg/'
    # driver= webdriver.Chrome()
    # driver.get(url)
    # f1(driver,18)
