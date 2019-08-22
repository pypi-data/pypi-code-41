import json


import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zlsrc.util.etl import  est_meta, est_html, add_info, est_gg



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="list_news_01"]//li[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('pageIndex=(\d+)',url)[0]

    if int(cnum) != num:
        url=re.sub('(?<=pageIndex=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//div[@class="list_news_01"]//li[1]/a').get_attribute('href')[-10:]

        driver.get(url)

        locator = (
            By.XPATH, '//div[@class="list_news_01"]//li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", class_="list_news_01").find('ul')

    dls = div.find_all("li",recursive=False)
    data = []
    for dl in dls:
        # print(dl)
        href=dl.find('a')['href']
        name=dl.find('a')['title']
        ggstart_time = dl.find('span',class_='date').get_text()
        href="http://www.ahhyzb.com.cn/"+href
        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//div[@class="list_news_01"]//li[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//div[@class="page_no"]/a[last()]').get_attribute('href')

    page_total=re.findall('pageIndex=(\d+)',page_total)[0]

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="display_content"][string-length()>100]')
    WebDriverWait(
        driver, 40).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', id='rightObj')

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.ahhyzb.com.cn/info.asp?second_id=3002&pageIndex=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://www.ahhyzb.com.cn/info.asp?second_id=3003&pageIndex=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_gqita_da_bian_gg" , 'http://www.ahhyzb.com.cn/info.asp?second_id=3005&pageIndex=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_liubiao_gg" , 'http://www.ahhyzb.com.cn/info.asp?second_id=3006&pageIndex=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


### 安徽寰亚国际招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=True,
        num=1,
        pageloadstrategy='none',long_ip=False
        )
    pass