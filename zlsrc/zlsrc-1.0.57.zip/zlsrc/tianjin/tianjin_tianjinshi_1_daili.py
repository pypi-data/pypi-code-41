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
    locator = (By.XPATH, '//div[@class="item title"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=int(re.findall('Page=(\d+)',url)[0])

    if int(cnum) != num:
        url=re.sub('(?<=Page=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//div[@class="item title"][1]//a').get_attribute('title')
        driver.get(url)
        locator = (
            By.XPATH, '//div[@class="item title"][1]//a[not(contains(@title,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find_all("div", class_="item title")

    data = []
    for dl in div:
        href=dl.find('a')['href']
        name=dl.find('a')['title']
        ggstart_time=dl.find('span',class_='date').get_text().strip('[').strip(']').strip()

        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//div[@class="item title"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//div[@class="simple-pager md light-theme simple-pagination"]/ul/li[last()-1]/a').get_attribute('href')

    page_total=re.findall('Page=(\d+)',page_total)[0]
    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="content"][string-length()>100]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.5)
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
    div = soup.find('div',class_="sub-category-bidding-detail")
    if div == None:
        raise ValueError('div is None')

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.tjpuze.com.cn/%E6%8B%9B%E6%A0%87%E4%BF%A1%E6%81%AF%E5%8F%91%E5%B8%83/%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A/?Page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhaobiao_1_gg" , 'http://www.tjpuze.com.cn/%E6%8B%9B%E6%A0%87%E4%BF%A1%E6%81%AF%E5%8F%91%E5%B8%83/%E9%87%87%E8%B4%AD%E5%85%AC%E5%91%8A/?Page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_gqita_da_bian_gg" , 'http://www.tjpuze.com.cn/%E6%8B%9B%E6%A0%87%E4%BF%A1%E6%81%AF%E5%8F%91%E5%B8%83/%E6%BE%84%E6%B8%85%E5%8F%8A%E4%BF%AE%E6%94%B9%E9%80%9A%E7%9F%A5/?Page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiaohx_gg" , 'http://www.tjpuze.com.cn/%E6%8B%9B%E6%A0%87%E4%BF%A1%E6%81%AF%E5%8F%91%E5%B8%83/%E8%AF%84%E6%A0%87%E7%BB%93%E6%9E%9C%E5%85%AC%E7%A4%BA/?Page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://www.tjpuze.com.cn/%E6%8B%9B%E6%A0%87%E4%BF%A1%E6%81%AF%E5%8F%91%E5%B8%83/%E9%87%87%E8%B4%AD%E7%BB%93%E6%9E%9C%E5%85%AC%E5%91%8A/?Page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###天津普泽工程咨询有限责任公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="天津市", **args)
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