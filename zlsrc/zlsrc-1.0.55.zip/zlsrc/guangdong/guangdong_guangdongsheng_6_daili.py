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
    locator = (By.XPATH, '//div[@class="list"]/ul[@class="ul"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('page=(\d+)',url)[0]

    if int(cnum) != num:
        url=re.sub('(?<=page=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//div[@class="list"]/ul[@class="ul"]/li[1]/a').get_attribute('href')[-20:]
        driver.get(url)
        locator = (
            By.XPATH, '//div[@class="list"]/ul[@class="ul"]/li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", class_="list").find('ul')
    dls = div.find_all("li")

    data = []
    for dl in dls:
        href=dl.find('a')['href']
        name=dl.find('a').get_text()
        diqu=dl.find('span').get_text().strip('[【').strip('】]')
        ggstart_time=dl.find('time').get_text()

        info=json.dumps({"diqu":diqu},ensure_ascii=False)

        href='http://www.hyzjs.com'+href
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="list"]/ul[@class="ul"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//a[@class="a_end"]').get_attribute('href')

    page_total=re.findall('page=(\d+)',page_total)[0]
    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="info_txt"][string-length()>100]')
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
    div = soup.find('div',class_="News_info")
    if div == None:
        raise ValueError('div is None')

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.hyzjs.com/zbgg/list_18.aspx?page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://www.hyzjs.com/zbggRK/list_19.aspx?page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###广东华禹工程咨询有限公司
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