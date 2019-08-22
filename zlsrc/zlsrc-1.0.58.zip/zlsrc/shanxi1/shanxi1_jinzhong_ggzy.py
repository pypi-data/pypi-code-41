import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_meta, est_html, add_info


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="article-list"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = re.findall('queryContent_(\d+)',url)[0]
    if num != cnum:
        url=re.sub('(?<=queryContent_)\d+',str(num),url)

        val = driver.find_element_by_xpath('//ul[@class="article-list"]/li[1]//a').get_attribute('href')

        driver.get(url)
        locator = (By.XPATH, '//ul[@class="article-list"]/li[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    ul = soup.find("ul", class_='article-list')

    lis = ul.find_all("li")

    data = []

    for li in lis:
        href = li.find("a")['href']
        name = li.find("a").get_text(strip=True)
        ggstart_time=li.find('div',class_='list-times').get_text()
        diqu=li.find('div',class_='article-list3-t2').find('div').label.get_text()
        info=json.dumps({'diuq':diqu},ensure_ascii=False)
        tmp=[name,ggstart_time,href,info]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="article-list"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//ul[@class="pages-list"]/li[1]').text
    total = re.findall("共\d+条记录 \d+/(\d+)页", total)[0]
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="div-article2"][string-length()>100]')

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

    div = soup.find('div', class_='div-content clearfix')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=81&ext=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=123&ext=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=83&ext=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=84&ext=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgys_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=85&ext=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=124&ext=",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=86&ext=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=87&ext=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=90&ext=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://ggzy.sxjz.gov.cn/queryContent_1-jyxx.jspx?title=&origin=&inDates=&channelId=88&ext=",["name", "ggstart_time", "href", "info"], f1, f2],

]

##晋中市公共资源交易网
def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省晋中市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "henan", "xinyang"], num=1, total=2, html_total=10,
         pageloadtimeout=60)