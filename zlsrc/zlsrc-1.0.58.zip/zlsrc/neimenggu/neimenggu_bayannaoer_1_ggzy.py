import json
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zlsrc.util.etl import est_meta, est_html, add_info

global xxtype_signal

def f1(driver, num):
    locator = (By.XPATH, "//ul[@id='showList']/li[last()]//a")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))

    cnum = driver.find_element_by_xpath("//div[@id='pagedt']//ul[@class='m-pagination-page']/li[@class='active']/a").text

    if int(cnum) != num:
        val = driver.find_element_by_xpath("//ul[@id='showList']/li[last()]//a").get_attribute('href')[-30:]
        locator = (By.XPATH, "//div[@id='pagedt']//div[@class='m-pagination-group']/input")
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located(locator)).clear()
        locator = (By.XPATH, "//div[@id='pagedt']//div[@class='m-pagination-group']/input")
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located(locator)).send_keys(num, Keys.ENTER)
        locator = (By.XPATH, "//ul[@id='showList']/li[last()]//a[not(contains(@href, '%s'))]"% val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find('ul', id='showList')
    lis = ul.find_all('li', class_='clearfix')
    data = []
    for li in lis:
        a = li.find('a')
        try:
            name = a['title']
        except:name = a.text.strip()
        href = a['href']
        if 'http' in href:
            href = href
        else:href = 'http://ggzyjy.bynr.gov.cn' + href
        ggstart_time = li.find('span', class_='r ewb-news-date').text.strip()

        temp = [name, ggstart_time, href]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    driver.refresh()
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@id='showList']/li[last()]//a")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_xpath("//div[@id='pagedt']//ul[@class='m-pagination-page']/li[last()]/a").text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='detail-body'][string-length()>30]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.5)
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
    div = soup.find('div', class_='ewb-list-main')
    # print(div)
    return div


def switch(driver, ggtype, xmtype):
    locator = (By.XPATH, "//ul[contains(@class, 'ewb-news-items')]/li[last()]//a")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    # try:
    #     val = driver.find_element_by_xpath("//div[@id='pagedt']//ul[@class='m-pagination-page']/li[last()]/a").text
    # except:
    #     val = driver.find_element_by_xpath("//div[@id='page']//ul[@class='m-pagination-page']/li[last()]/a").text

    # if ggtype != "建设工程":
    #     driver.find_element_by_xpath("//ul[@class='l ewb-overstory-items']/li[contains(string(),'%s')]" % ggtype).click()
    #
    #     locator = (By.XPATH, "//ul[@class='l ewb-overstory-items']/li[@class='current' and contains(string(),'%s')]" % ggtype)
    #     WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    #
    #     locator = (By.XPATH, "//div[@id='pagedt']//ul[@class='m-pagination-page']/li[last()]/a[not(contains(string(),'%s'))]" % val)
    #     WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    try:
        val = driver.find_element_by_xpath("//div[@id='pagedt']//ul[@class='m-pagination-page']/li[last()]/a").text
    except:
        val = driver.find_element_by_xpath("//div[@id='page']//ul[@class='m-pagination-page']/li[last()]/a").text

    driver.find_element_by_xpath("//div[@style='display: block;']//ul[@class='cate-drop' and @data-target='cate']/li[contains(string(),'%s')]" % xmtype).click()
    time.sleep(1)
    locator = (
    By.XPATH, "//div[@style='display: block;']//ul[@class='cate-drop' and @data-target='cate']/li[contains(@class, 'active') and contains(string(),'%s')]" % xmtype)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))

    locator = (By.XPATH, "//div[@id='pagedt']//ul[@class='m-pagination-page']/li[last()]/a[not(contains(string(),'%s'))]" % val)
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))



def before(f, ggtype, xmtype):
    def wrap(*args):
        driver = args[0]
        switch(driver, ggtype, xmtype)
        return f(*args)

    return wrap


data = [

    ["gcjs_zhaobiao_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018001/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "招标公告"), before(f2, "建设工程", "招标公告")],

    ["gcjs_biangeng_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018001/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "变更公告"), before(f2, "建设工程", "变更公告")],

    ["gcjs_gqita_zhaobiaowenjian_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018001/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(add_info(f1, {'gglx':'招标文件'}), "建设工程", "招标文件"), before(f2, "建设工程", "招标文件")],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018001/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "澄清补疑"), before(f2, "建设工程", "澄清补疑")],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018001/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "中标候选人公示"), before(f2, "建设工程", "中标候选人公示")],

    ["gcjs_zhongbiao_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018001/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "中标公告"), before(f2, "建设工程", "中标公告")],

    ["gcjs_liubiao_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018001/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "招标异常"), before(f2, "建设工程", "招标异常")],
    #######
    ["zfcg_dyly_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018002/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "单一来源公示"), before(f2, "政府采购", "单一来源公示")],

    ["zfcg_zhaobiao_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018002/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "采购公告"), before(f2, "政府采购", "采购公告")],

    ["zfcg_biangeng_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018002/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "变更公告"), before(f2, "政府采购", "变更公告")],

    ["zfcg_zgys_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018002/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "资格预审公告"), before(f2, "政府采购", "资格预审公告")],

    ["zfcg_zhongbiao_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018002/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "中标公告"), before(f2, "政府采购", "中标公告")],

    ["zfcg_liubiao_gg",
     "http://ggzyjy.bynr.gov.cn/jyxx/018002/tradeInfoMore.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "废标公告"), before(f2, "政府采购", "废标公告")],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区巴彦淖尔市", **kwargs)
    est_html(conp, f=f3, **kwargs)



if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "bayannaoer"])
    #
    # driver = webdriver.Chrome()
    # for d in data[-5:]:
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = d[-1](driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     df=d[-2](driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
