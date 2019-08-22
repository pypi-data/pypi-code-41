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
    # val = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='n_news']/ul/li/div/div/a"))).get_attribute('href')[-10:]
    # # print(val)
    # cnum = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='box']/a[4]"))).text

    # # print(cnum)
    # if int(cnum) != int(num):
    new_url = re.sub('p=\d+', 'p=' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, "//div[@class='n_news']/ul/li/div/div/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='n_news']/ul/li/div/div")
    for content in content_list:
        name = content.xpath("./a/h1/text()")[0].strip()
        ggstart_time = content.xpath("./div/strong/text()")[0].strip()
        url = 'http://www.sxzx2016.com/index.php?m=Article&a=index' + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    driver.maximize_window()
    href_temp = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//div[@id='n_right']/div[3]/div/a[last()]"))).get_attribute('href')
    total_page = href_temp.rsplit('=', 1)[-1]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='n_article']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', id="n_article")
    return div


data = [
     ["qycg_zhaobiao_gg",
     "http://www.sxzx2016.com/index.php?m=Article&a=index&id=38&p=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiao_gg",
     "http://www.sxzx2016.com/index.php?m=Article&a=index&id=40&p=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]
####中昕国际建设咨询集团
def work(conp, **args):
    est_meta(conp, data=data, diqu="中昕国际建设咨询集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "qycg_www_sxzx2016_com"]
    work(conp)

    # for d in data:
    #     print(d[1])
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

    # url = 'http://www.sxzx2016.com/index.php?m=Article&a=index&id=38&p=3'
    # driver= webdriver.Chrome()
    # driver.get(url)
    # f1(driver,18)





