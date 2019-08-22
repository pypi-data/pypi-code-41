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
    locator = (By.XPATH, '//ul[@class="news_list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('pageNo=(\d+)',url)[0]

    if int(cnum) != num:
        url=re.sub('(?<=pageNo=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//ul[@class="news_list"]/li[1]/a').get_attribute('href')[-30:]
        driver.get(url)
        locator = (
            By.XPATH, '//ul[@class="news_list"]/li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", class_="news_list")
    dls = div.find_all("li")

    data = []
    for dl in dls:
        href=dl.find('a')['href']
        name=dl.find('a')['title']
        ggstart_time=dl.find('span',class_='time').get_text()

        href='http://www.hlcec.com/'+href
        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//ul[@class="news_list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//span[@class="blue"][last()]/a').get_attribute('href')

    page_total=re.findall('pageNo=(\d+)',page_total)[0]
    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="detail_content new_link"][string-length()>100]')
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
    div = soup.find('div',class_="detail_content new_link")
    if div == None:
        raise ValueError('div is None')

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.hlcec.com/invite/channel2.do?formMap.id=ff808081589030f30158a8ede2a10a79&pageNo=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiaohx_gg" , 'http://www.hlcec.com/invite/channel2.do?formMap.id=ff808081589030f30158a8ef896e0a7b&pageNo=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://www.hlcec.com/invite/channel2.do?formMap.id=ff808081589030f30158a8f043400a7c&pageNo=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_gqita_da_bian_gg" , 'http://www.hlcec.com/invite/channel2.do?formMap.id=ff808081589030f30158a8ee36ab0a7a&pageNo=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###华联世纪工程咨询股份有限公司
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