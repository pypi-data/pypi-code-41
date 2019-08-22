import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_tbs, est_meta, est_html



def f1(driver, num):
    locator = (By.XPATH, '//table[@id="ctl00_ContentPlaceHolder2_DataList1"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_xpath('//span[@id="ctl00_ContentPlaceHolder2_A2"]').text)

    if int(cnum) != int(num):
        while True:
            cnum = int(driver.find_element_by_xpath('//span[@id="ctl00_ContentPlaceHolder2_A2"]').text)
            val = driver.find_element_by_xpath(
                '//table[@id="ctl00_ContentPlaceHolder2_DataList1"]/tbody/tr[1]//a').get_attribute('href')[-55:]

            if cnum > num:
                if cnum - num > page_total // 2:
                    first_b = driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_F1"]')
                    driver.execute_script("arguments[0].click()", first_b)
                else:
                    pre_b = driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_F2"]')
                    driver.execute_script("arguments[0].click()", pre_b)

            elif cnum < num:
                if num - cnum > page_total // 2:
                    last_b = driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_F4"]')
                    driver.execute_script("arguments[0].click()", last_b)
                else:
                    nex_b = driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_F3"]')
                    driver.execute_script("arguments[0].click()", nex_b)

            else:
                break

            # 第二个等待
            locator = (By.XPATH,
                       '//table[@id="ctl00_ContentPlaceHolder2_DataList1"]/tbody/tr[1]//a[not(contains(@href,"{}"))]'.format(
                           val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='ctl00_ContentPlaceHolder2_DataList1').find('tbody').find_all('tr', recursive=False)

    for tr in div:

        href = tr.find('a')['href']
        name = tr.find('a').get_text(strip=True)
        jytype=tr.find('a').find_all('span')[0].get_text()
        gctype=tr.find('a').find_all('span')[-1].get_text()
        gctype=re.findall('【(.+?)】',gctype)

        if gctype:
            info = json.dumps({'jytype': jytype, 'gctype': gctype[0]}, ensure_ascii=False)
        else:
            info = json.dumps({'jytype': jytype}, ensure_ascii=False)

        ggstart_time = tr.find_all('nobr')[-1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.cqbnggzyjy.com/LBv3/' + href


        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    global page_total
    locator = (By.XPATH, '//table[@id="ctl00_ContentPlaceHolder2_DataList1"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page_total = int(driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_T1"]').get_attribute('value'))
    except:
        page_total=int(driver.find_element_by_xpath('//span[@id="ctl00_ContentPlaceHolder2_A1"]').text)

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@class="bk3"][string-length()>200]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    before = len(driver.page_source)
    time.sleep(0.5)
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

    div = soup.find('table', class_="bk3")

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["jqita_zhaobiao_gg", "http://www.cqbnggzyjy.com/LBv3/n_newslist_zb_item_all.aspx",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_da_bian_gg", "http://www.cqbnggzyjy.com/LBv3/n_newslist_item_all.aspx",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiaohx_gg", "http://www.cqbnggzyjy.com/LBv3/n_newslist_zz_item_all.aspx",["name", "ggstart_time", "href", "info"], f1, f2],



]


def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆市巴南区", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "banan"], total=2, headless=False, num=1)



