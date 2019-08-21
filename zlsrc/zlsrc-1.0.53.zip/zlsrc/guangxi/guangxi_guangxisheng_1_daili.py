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

# 点击翻页
# http://www.gxtzfz.cn/Notice.aspx?TypeID=14  翻页前
# http://www.gxtzfz.cn/Notice.aspx?TypeID=14  翻页后
# http://www.gxtzfz.cn/NoticeShow.aspx?ArticleID=4428&TypeID=14  详情页

def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='newslist']/li/a")
    val= WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
    locator = (By.XPATH, "//div[@id='page']//span[2]")
    cnum = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text  #获取当前页的页码
    if int(cnum) != int(num):    #定位输入框、跳转按钮；
        driver.find_element_by_xpath("//input[@id='ctl00_cphBannerAndMain_PageControls1_txtGoPage']").clear()  #清空输入框
        driver.find_element_by_xpath("//input[@id='ctl00_cphBannerAndMain_PageControls1_txtGoPage']").send_keys(num)  #num为要跳转的页码
        driver.find_element_by_xpath("//input[@value='跳转']").click()  #点击跳转按钮
        locator = (By.XPATH, "//ul[@class='newslist']/li/a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    # return
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='newslist']/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()   #定位name
        ggstart_time = content.xpath("./span/text()")[0].strip()  #定位time
        url = 'http://www.gxtzfz.cn/Notice.aspx?TypeID=14' + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):   # 求总页数
    total_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//div[@id='page']/table//span[5]"))).text
    driver.quit()
    return int(total_page)


def f3(driver, url):  #详情页的定位
    driver.get(url)
    locator = (By.XPATH, "//div[@id='about_cont']")
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
    div = soup.find('div', id="about_cont")
    return div

data = [
     ["jqita_zhaobiao_gg","http://www.gxtzfz.cn/Notice.aspx?TypeID=14",["name", "ggstart_time", "href", "info"], f1, f2],
     ["jqita_zhongbiao_gg","http://www.gxtzfz.cn/Notice.aspx?TypeID=62",["name", "ggstart_time", "href", "info"], f1, f2],
     ["jqita_zhongbiaohx_gg","http://www.gxtzfz.cn/Notice.aspx?TypeID=64",["name", "ggstart_time", "href", "info"], f1, f2],
     ["jqita_biangeng_gg","http://www.gxtzfz.cn/Notice.aspx?TypeID=63",["name", "ggstart_time", "href", "info"], f1, f2],

]
#  广西同泽工程项目管理有限责任公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "jqita_www_gxtzfz_cn"]
    work(conp)

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
    #         # print(f3(driver, item_list[0][2]))
    #         driver.get(d[1])
    #     driver.quit()

    # url = 'http://www.gxtzfz.cn/Notice.aspx?TypeID=14'
    # driver= webdriver.Chrome()
    # driver.get(url)
    # f1(driver,10)


