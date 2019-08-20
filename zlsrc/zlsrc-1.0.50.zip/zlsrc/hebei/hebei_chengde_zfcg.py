import json

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html



def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, "//div[@class='detail']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', class_="detail")
    return div


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="datagrid-view"]/div[@class="datagrid-view2"]/div/table/tbody/tr/td/div/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-15:]

    locator = (By.XPATH, '//input[@class="pagination-num"]')
    cnum = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('value')
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        driver.find_element_by_xpath('//input[@class="pagination-num"]').clear()
        driver.find_element_by_xpath('//input[@class="pagination-num"]').send_keys(num)
        driver.find_element_by_xpath('//input[@class="pagination-num"]').send_keys(Keys.ENTER)

        locator = (By.XPATH, '//div[@class="datagrid-view"]/div[@class="datagrid-view2"]/div/table/tbody/tr/td/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content1_list = body.xpath('//div[@class="datagrid-view1"]/div[@class="datagrid-body"]/div/table/tbody/tr')
    content2_list = body.xpath('//div[@class="datagrid-view2"]/div[@class="datagrid-body"]/table/tbody/tr')
    for content1,content2 in zip(content1_list,content2_list):
        xm_code = content1.xpath("./td[2]/div/text()")[0].strip()
        name = content2.xpath('./td/div/a/text()')[0].strip()
        url = 'http://sl.ggzyjyw.com' + content2.xpath('./td/div/a/@href')[0].strip()
        ggstart_time = content2.xpath('./td[2]/div/text()')[0].strip()

        gytype = content2.xpath('./td[4]/div/text()')[0].strip()
        gymethod = content2.xpath('./td[5]/div/text()')[0].strip()


        json.dumps({'xm_code':xm_code,'gytype':gytype,'gymethod':gymethod})
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] =None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="datagrid-view"]/div[@class="datagrid-view2"]/div/table/tbody/tr/td/div/a')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text

    locator = (By.XPATH, '//span[@style="padding-right:6px;"]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('(\d+)',txt)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg",
     "http://sl.ggzyjyw.com/deallist/2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="河北省承德市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "hebei_chengde"])
    # driver =webdriver.Chrome()
    # url = "http://sl.ggzyjyw.com/deal/b011a0d48ef.shtml"
    # # driver.get(url)
    # f1(driver,2)
    # f1(driver,4)
    # print(f3(driver,url))