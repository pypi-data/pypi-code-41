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
    new_url = re.sub('list_12_\d+', 'list_12_' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, "//div[@class='right clear']/div/p")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='right clear']/div/p[1]")
    for content in content_list:
        try:
            try:
                name = content.xpath("./a[last()]/b/text()")[0]
            except:
                name = content.xpath("./a[last()]/text()")[0]
        except:
            name = '-'
        # print(name)
        # url_temp = content.xpath("./a/@href")[0]
        #         # if
        ggstart_time = content.xpath("./a/span/text()")[0]
        url = 'http://www.gzsuike.com' + content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):   # 求总页数

    locator = (By.XPATH,"//div[@class='tg_pages']//li[last()-1]/a")
    href_temp = WebDriverWait(driver,20).until(EC.presence_of_element_located(locator)).get_attribute('href')
    # print(href_temp)
    href_temp = href_temp.rsplit('_', 1)[-1]
    total_page = re.findall('\d+', href_temp)[0]  #把总页数截取出来
    # print(total_page)
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//article[@class='zw clear']")
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
    div = soup.find('article', class_="zw clear")
    return div

data = [
     ["jqita_zhaobiao_gg",
     "http://www.gzsuike.com/a/zhaobiaocaigou/zhaobiaogonggao/list_12_1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.gzsuike.com/a/zhaobiaocaigou/zhongbiaogongshi/list_13_3.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]
# 广州穗科建设管理有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "jqita_www_gzsuike_com"]
    work(conp,retry=3,thread_retry=3)

    # for d in data:
    #     # print(d[1])
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     for i in range(1,total,5):
    #         print(i)
    #         df = f1(driver,i)
    #         item_list = df.values.tolist()
    #
    #         print(f3(driver, item_list[0][2]))
    #         driver.get(d[1])
    #     driver.quit()

    # url = 'http://www.sxzx2016.com/index.php?m=Article&a=index&id=38&p=3'
    # driver= webdriver.Chrome()
    # driver.get(url)
    # f1(driver,18)

