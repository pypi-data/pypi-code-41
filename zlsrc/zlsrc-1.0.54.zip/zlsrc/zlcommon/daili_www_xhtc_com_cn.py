import json
import random
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='tenderlist']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//span[@class='current']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='tenderlist']/li[last()]/a").get_attribute('href')[-12:]
        url = re.sub('p=[0-9]+', 'p=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='tenderlist']/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('ul', class_='tenderlist')
    lis = table.find_all('li')
    for tr in lis:
        a = tr.find('a')

        name = tr.find('div', class_='tenderdiv').text.strip()
        ggstart_time = tr.find('span', class_='tenderspan').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.xhtc.com.cn/' + link

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='tenderlist']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    while True:
        val = driver.find_element_by_xpath("//ul[@class='tenderlist']/li[last()]/a").get_attribute('href')[-12:]
        try:
            locator = (By.XPATH, "//div[@class='ljl_pagebox']/a[contains(string(), '下一页')]")
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).click()
        except:
            locator = (By.XPATH, "//div[@class='ljl_pagebox']/a[contains(string(), '上一页')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            break
        locator = (By.XPATH, "//ul[@class='tenderlist']/li[last()]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    num = driver.find_element_by_xpath("//span[@class='current']").text.strip()
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='tenderp'][string-length()>60]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='tenderp').parent
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_gqita_zhao_zhong_gg",
     "http://www.xhtc.com.cn/tenders.html?&p=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

#新华招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="新华招标有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_xhtc_com_cn"], )


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


