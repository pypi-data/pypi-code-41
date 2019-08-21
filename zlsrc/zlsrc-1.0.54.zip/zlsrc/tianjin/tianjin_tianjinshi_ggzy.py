import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta
import time



def f1(driver, num):
    locator = (By.XPATH, "//div[@class='pages']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//div[@class='pages']/ul/li[1]/a").text
    cnum = re.findall("(\d+)\/", page_temp)[0]

    locator = (By.XPATH, "//ul[@class='article-list2']/li")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='article-list2']/li/div/a").get_attribute("href")[-30:]
    # print("cnum",cnum,"val",val)
    if int(cnum) != int(num):
        url = re.sub("Content[\w_]{0,}-","Content_"+str(num)+'-',driver.current_url)

        # print(url)
        driver.get(url)
        locator = (
            By.XPATH, '//ul[@class="article-list2"]/li/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.CLASS_NAME, 'article-list2')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='article-list2']/li")
    for j,content in enumerate(content_list):
        name = content.xpath("./div/a")[0].xpath("string(.)").strip()

        ggstart_time = content.xpath("./div/div/text()")[0].strip()
        driver.find_element_by_xpath("//ul[@class='article-list2']/li[%s]"%(j+1)).click()
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        url = driver.current_url
        driver.close()
        driver.switch_to.window(windows[0])
        # url = content.xpath("./div/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pages']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//div[@class='pages']/ul/li[1]/a").text
    total_page = re.findall("\/(\d+)", page_temp)[0]

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.ID, "content")
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
    soup = BeautifulSoup(page, 'lxml')
    div = soup.find('div', id='content')
    return div


data = [
    ["zfcg_yucai_gg",
     "http://ggzy.xzsp.tj.gov.cn/queryContent-jyxx.jspx?title=&inDates=&ext=&ext1=&origin=&channelId=86&beginTime=&endTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg",
     "http://ggzy.xzsp.tj.gov.cn/queryContent-jyxx.jspx?title=&inDates=&ext=&ext1=&origin=&channelId=87&beginTime=&endTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://ggzy.xzsp.tj.gov.cn/queryContent-jyxx.jspx?title=&inDates=&ext=&ext1=&origin=&channelId=90&beginTime=&endTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.xzsp.tj.gov.cn/queryContent-jyxx.jspx?title=&inDates=&ext=&ext1=&origin=&channelId=88&beginTime=&endTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://ggzy.xzsp.tj.gov.cn/queryContent-jyxx.jspx?title=&inDates=&ext=&ext1=&origin=&channelId=81&beginTime=&endTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzy.xzsp.tj.gov.cn/queryContent-jyxx.jspx?title=&inDates=&ext=&ext1=&origin=&channelId=83&beginTime=&endTime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="天津市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "tianjin", "tianjin"]
    work(conp)


    # url = "http://ggzy.xzsp.tj.gov.cn/queryContent-jyxx.jspx?title=&inDates=&ext=&ext1=&origin=&channelId=86&beginTime=&endTime="
    # d = webdriver.Chrome()
    # d.get(url)
    # # print(f2(d))
    # f1(d,1)
    # f1(d,5)
    # d.quit()