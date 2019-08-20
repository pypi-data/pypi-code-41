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
    locator = (By.XPATH, '//div[@id="msgList"]//ul[@class="list-ul"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//li[@class="active"]').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//div[@id="msgList"]//ul[@class="list-ul"]/li[1]//a').get_attribute('href')[-30:]

        search_button = driver.find_element_by_xpath('//input[@class="default_pgCurrentPage"]')
        driver.execute_script("arguments[0].value='%s';" % num, search_button)
        ele = driver.find_element_by_xpath('//li[@class="default_pgJump active"]')
        driver.execute_script("arguments[0].click()", ele)

        locator = (
            By.XPATH, '//div[@id="msgList"]//ul[@class="list-ul"]/li[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", id="msgList").find('ul',class_='list-ul')
    dls = div.find_all("li")
    data = []
    for dl in dls:

        href=dl.find('a')['href']
        name=dl.find('a').span['title']
        ggstart_time = dl.find('span',class_='timedate').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.chongchuan.gov.cn' + href

        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="msgList"]//ul[@class="list-ul"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//span[@class="default_pgTotalPage"]').text

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="zoom"][string-length()>100]')
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
    div = soup.find('div', class_='con')

    return div



data=[

["zfcg_zhaobiao_gg" , 'http://www.chongchuan.gov.cn/ccqrmzf/zbgg/zbgg.html', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhongbiao_gg" , 'http://www.chongchuan.gov.cn/ccqrmzf/zhbgg/zhbgg.html', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###南通市崇川区人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省南通市崇川区", **args)
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