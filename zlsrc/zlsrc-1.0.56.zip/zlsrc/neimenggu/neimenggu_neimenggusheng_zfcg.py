import json

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html, add_info



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='center'][string-length()>50]")
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
    div = soup.find('div', id='center')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="itemContainer"]/tbody/tr[1]//a')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))

    url = driver.current_url
    cnum = driver.find_element_by_xpath('//a[@class="jp-disabled"]').text.strip()

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//table[@id="itemContainer"]/tbody/tr[1]//a').get_attribute('href')[-15:]
        Select(driver.find_element_by_xpath('//div[@class="holder"]/select')).select_by_value('%d'%num)
        locator = (By.XPATH, '//table[@id="itemContainer"]/tbody/tr[1]//a[not(contains(@href, "%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find('table', id='itemContainer').tbody
    trs = tbody.find_all('tr')
    for tr in trs:
        a = tr.find('a')
        name = a['title']
        href = a['href']
        if 'http' in href:
            url = href
        else:
            url = "http://www.nmgp.gov.cn" + href
        ggstart_time = tr.find('td', class_='feed-time').span.text.strip()
        ggstart_time = re.findall(r'[0-9]{4}[-/][0-9]{,2}[-/][0-9]{,2}', ggstart_time)[0]

        area = tr.find_all('td')[1].span.text.strip()
        category = tr.find_all('td')[2].span.text.strip()
        info = json.dumps({'area':area,'category':category},ensure_ascii=False)
        temp = [name, ggstart_time, url, info]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="holder"]/a[last()-1]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = driver.find_element_by_xpath('//div[@class="holder"]/a[last()-1]').text
    driver.quit()
    return int(total_page)


def click_gg(driver, ggtype):
    val = driver.find_element_by_xpath('//*[@id="itemContainer"]/tbody/tr[1]//a').get_attribute("href")[-30:]
    driver.find_element_by_xpath(
        '//li[1]//ul[@class="spread-item fast-nav-list fast-nav-list-2 mt mb"]/li/a[contains(string(),"%s")]' % ggtype).click()
    locator = (By.XPATH, '//table[@id="itemContainer"]//tr[1]//a[not(contains(string(),"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))


def before(f, ggtype):
    def wrap(*args):
        driver = args[0]
        driver.get("http://www.nmgp.gov.cn/category/cggg?type_name=1")
        click_gg(driver, ggtype)
        return f(*args)

    return wrap


data = [
    #
    ["zfcg_zhaobiao_gg",
     "http://www.nmgp.gov.cn/category/cggg?type_name=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_zhao_gg",
     "http://www.nmgp.gov.cn/category/cggg?type_name=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'招标更正公告'}), f2],

    ["zfcg_zhongbiao_gg",
     "http://www.nmgp.gov.cn/category/cggg?type_name=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_zhong_gg",
     "http://www.nmgp.gov.cn/category/cggg?type_name=4",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'中标(成交)更正公告'}), f2],

    ["zfcg_liubiao_gg",
     "http://www.nmgp.gov.cn/category/cggg?type_name=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zgys_gg",
     "http://www.nmgp.gov.cn/category/cggg?type_name=6",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_zs_gg",
     "http://www.nmgp.gov.cn/category/cggg?type_name=7",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'资格预审更正公告'}),f2],

    ["zfcg_dyly_gg",
     "http://www.nmgp.gov.cn/category/dyly",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="内蒙古自治区", **arg)
    est_html(conp, f=f3, **arg)

# 修改日期：2019/8/20
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "neimenggu"],num=1)


    # for d in data[4:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     for i in range(11, 15):
    #         df=f1(driver, i)
    #         print(df.values)
        # for f in df[2].values:
        #     d = f3(driver, f)
        #     print(d)