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
    locator = (By.XPATH, '//div[@id="newslist"]/ul/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=int(re.findall('page=(\d+)',url)[0])+1

    if int(cnum) != num:
        url=re.sub('(?<=page=)\d+',str(num-1),url)
        val = driver.find_element_by_xpath(
            '//div[@id="newslist"]/ul/li[1]//a').get_attribute('href')[-20:]
        driver.get(url)
        locator = (
            By.XPATH, '//div[@id="newslist"]/ul/li[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", id="newslist").find('ul')
    dls = div.find_all("li")

    data = []
    for dl in dls:
        href=dl.find('a')['href'].strip('.')
        name=dl.find('a').get_text(strip=True)
        ggstart_time=dl.find('span',class_='f03').get_text()

        href='http://www.gzgxgw.com'+href
        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//div[@id="newslist"]/ul/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_link_text('最后页').get_attribute('href')

    page_total=re.findall('page=(\d+)',page_total)[0]
    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="textcon"][string-length()>100]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.5)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.5)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div',class_="textcon").parent
    if div == None:
        raise ValueError('div is None')

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.gzgxgw.com/daili_contract.asp?classcode=001300060001&page=0', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://www.gzgxgw.com/daili_contract.asp?classcode=001300060002&page=0', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiaohx_gg" , 'http://www.gzgxgw.com/daili_contract.asp?classcode=001300060003&page=0', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_biangeng_gg" , 'http://www.gzgxgw.com/daili_contract.asp?classcode=001300060004&page=0', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###广州高新工程顾问有限公司﻿
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
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
        )
    pass