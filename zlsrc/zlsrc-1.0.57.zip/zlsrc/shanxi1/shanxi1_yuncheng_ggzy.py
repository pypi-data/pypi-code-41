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
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = re.findall('Paging=(\d+)',url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//ul[@class="wb-data-item"]/li[1]//a').get_attribute('href')[-40:-20]

        url=re.sub('(?<=Paging=)\d+',str(num),url)
        driver.get(url)

        locator = (
            By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", class_='wb-data-item')
    dls = div.find_all("li")
    data = []
    for dl in dls:

        href=dl.find('a')['href']
        name=dl.find('a')['title'].strip()

        ggstart_time = dl.find('span',class_='wb-data-date').get_text()

        href="http://ggzyjyzx.yuncheng.gov.cn"+href

        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total=driver.find_element_by_xpath('//td[@class="huifont"]').text
        total=re.findall('\d/(\d+)',total)[0]
    except:
        total=1
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="mainContent"][string-length()>100]')
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
    div = soup.find('div', class_='article-block')

    return div



data=[

["gcjs_zhaobiao_gg" , 'http://ggzyjyzx.yuncheng.gov.cn/TPFront/jyxx/005001/005001001/?Paging=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_biangeng_gg" , 'http://ggzyjyzx.yuncheng.gov.cn/TPFront/jyxx/005001/005001002/?Paging=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiaohx_gg" , 'http://ggzyjyzx.yuncheng.gov.cn/TPFront/jyxx/005001/005001003/?Paging=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiao_gg" , 'http://ggzyjyzx.yuncheng.gov.cn/TPFront/jyxx/005001/005001004/?Paging=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

["zfcg_zhaobiao_gg" , 'http://ggzyjyzx.yuncheng.gov.cn/TPFront/jyxx/005002/005002001/?Paging=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_biangeng_gg" , 'http://ggzyjyzx.yuncheng.gov.cn/TPFront/jyxx/005002/005002002/?Paging=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhongbiao_gg" , 'http://ggzyjyzx.yuncheng.gov.cn/TPFront/jyxx/005002/005002003/?Paging=1', ["name", "ggstart_time", "href", 'info'],f1, f2],


      ]




###运城市公共资源交易中心
def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省运城市", **args)
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