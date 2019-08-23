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
    locator = (By.XPATH, '//td[@class="wz"]/table[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('page=(\d+)',url)[0]

    if int(cnum) != num:
        url=re.sub('(?<=page=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//td[@class="wz"]/table[1]//a').get_attribute('href')[-30:]
        driver.get(url)
        locator = (
            By.XPATH, '//td[@class="wz"]/table[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("td", class_="wz")

    dls = div.find_all("table")
    data = []
    for dl in dls:
        # print(dl)
        href=dl.find('a')['href']
        name=dl.find('a').get_text(strip=True)
        ggstart_time = dl.find('div',class_='date').get_text()
        ggstart_time=ggstart_time.split('\xa0')[0].strip('发布时间：')
        href='http://www.sfcx.cn/'+href
        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//td[@class="wz"]/table[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//div[@class="message"]/i[2]').text

    page_total=re.findall('/.?(\d+)',page_total)[0]

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@width="1170"]/tbody/tr/td[@align="left"][@valign="top"][string-length()>100]')
    WebDriverWait(
        driver, 10).until(
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
    div = soup.find('td',class_="wz").parent.parent.parent
    if div == None:
        raise ValueError('div is None')

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.sfcx.cn/purchase.aspx?ClassID=23&BID=&Keywords=&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiaohx_gg" , 'http://www.sfcx.cn/purchase.aspx?ClassID=25&BID=&Keywords=&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_gqita_da_bian_gg" , 'http://www.sfcx.cn/purchase.aspx?ClassID=24&BID=&Keywords=&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###广东三方诚信招标有限公司﻿
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    # work(
    #     conp=[
    #         "postgres",
    #         "since2015",
    #         '192.168.3.171',
    #         "zhixiashi",
    #         "beijing"],
    #     headless=True,
    #     num=1,
    #     )
    pass
    url="http://www.sfcx.cn/ShowInfo.aspx?id=40019"
    driver=webdriver.Chrome()
    f3(driver,url)
