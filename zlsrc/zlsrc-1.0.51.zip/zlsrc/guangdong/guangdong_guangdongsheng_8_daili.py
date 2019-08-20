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

    locator = (By.XPATH, '//ul[@class="pur_l"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=int(re.findall('page=(\d+)',url)[0])

    if int(cnum) != num:
        url=re.sub('(?<=page=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//ul[@class="pur_l"]/li[1]/a').get_attribute('href')[-20:]
        driver.get(url)
        locator = (
            By.XPATH, '//ul[@class="pur_l"]/li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", class_="pur_l")
    dls = div.find_all("li")

    data = []
    for dl in dls:
        href=dl.find('a')['href']
        name=dl.find('a')['title']
        ggstart_time=dl.find('em').get_text()

        href='http://www.gdhwjl.com/'+href
        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):


    while True:
        locator = (By.XPATH, '//ul[@class="pur_l"]/li[1]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            totalpageurl=driver.find_element_by_xpath('//div[@class="sabrosus"]/a[last()-1]').get_attribute('href')
            current=driver.find_element_by_xpath('//a[@class="current"]').text
        except:
            current=1
            break

        totalpage=re.findall('page=(\d+)',totalpageurl)[0]
        if int(current) > int(totalpage):
            break
        driver.get(totalpageurl)
        time.sleep(0.5)

    page_total=current
    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="art_cent"][string-length()>100]')
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
    div = soup.find('div',class_="page_c")
    if div == None:
        raise ValueError('div is None')

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.gdhwjl.com/purchase.php?type=nav6&not=70&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_gqita_da_bian_gg" , 'http://www.gdhwjl.com/purchase.php?type=nav6&not=71&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zsjg_gg" , 'http://www.gdhwjl.com/purchase.php?type=nav6&not=72&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiaohx_gg" , 'http://www.gdhwjl.com/purchase.php?type=nav6&not=73&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://www.gdhwjl.com/purchase.php?type=nav6&not=74&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###广东海外建设咨询有限公司﻿
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