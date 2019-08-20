import random
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large


def f1(driver, num):
    locator = (By.XPATH, "//table[@width='100%']/tbody/tr[2]/td[@class='xin2zuo']//tr[@height='20'][last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//table[@width='100%']/tbody/tr[3]/td[@class='xin2zuo']")
    total_page = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'第(\d+)页', total_page)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@width='100%']/tbody/tr[2]/td[@class='xin2zuo']//tr[@height='20'][last()]//a").get_attribute('href')[-30:]
        driver.find_element_by_xpath("//input[@id='pagenum']").clear()
        driver.find_element_by_xpath("//input[@id='pagenum']").send_keys(num)
        driver.find_element_by_xpath("//input[@value='go']").click()

        locator = (By.XPATH, "//table[@width='100%']/tbody/tr[2]/td[@class='xin2zuo']//tr[@height='20'][last()]//a[not(contains(@href,'{}'))]".format(val))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    td = soup.find('td', class_='xin2zuo')
    lis = td.find_all('tr', height='20')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('td', width='12%')[-1].text.strip()
        ggstart_time = re.findall(r'\[(.*)\]', ggstart_time)[0]
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.hnsl.gov.cn/' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@width='100%']/tbody/tr[3]/td[@class='xin2zuo']")
    total_page = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'共(\d+)页', total_page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@id='content6'][string-length()>140]")
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
    div = soup.find('td', valign="top")
    return div


data = [

    ["gcjs_zhaobiao_gg",
     "http://www.hnsl.gov.cn/viewCmsCac.do?cacId=ff8080812af70391012af9b376fe00e9",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["gcjs_zhongbiaohx_gg",
     "http://www.hnsl.gov.cn/viewCmsCac.do?cacId=ff8080812af70391012af9b3770e00ea",
     ["name", "ggstart_time", "href", "info"],f1 ,f2],

]

##河南省水利网,河南省水利厅
def work(conp, **args):
    est_meta_large(conp, data=data, diqu="河南省﻿", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_hnsl_gov_cn"])


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


