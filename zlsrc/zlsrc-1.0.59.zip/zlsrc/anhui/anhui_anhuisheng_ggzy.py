from pprint import pprint

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
from zlsrc.util.etl import est_html, gg_existed, add_info, est_meta_large


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="list_title"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_xpath('//a[@class="thispage"]').text)

    if int(cnum) != int(num):
        val = driver.find_element_by_xpath('//div[@class="list_title"]//li[1]/a').get_attribute('href')[-20:]
        driver.execute_script("GoToPage('%s')" % num)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="list_title"]//li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs1 = soup.find('div', class_="list_title").find_all('li')
    trs2 = soup.find('div', class_="contlist_date").find_all('li')

    for i in range(len(trs1)):
        tr1 = trs1[i]
        tr2 = trs2[i]

        href = tr1.find('a')['href']
        name = tr1.find('a')['title']
        ggstart_time = tr2.get_text(strip=True)

        if 'http' in href:
            href = href
        else:
            href = 'http://www.ahbc.com.cn/' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="list_title"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = re.findall('页码不能大于(\d+)', driver.page_source)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="content_article"][string-length()>50]')
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

    div = soup.find('div', class_="provincial_content")
    try:
        div.find('div', id='divAd').extract()
    except:
        pass

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["qsy_zhaobiao_gg", "http://www.ahbc.com.cn/exclusive.aspx?type=qy", ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qsy_zhaobiao_wt_gg", "http://www.ahbc.com.cn/exclusive.aspx?type=wt", ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': "委托招标"}),
     f2],
    ["gcjs_zhaobiao_diqu1_gg", "http://www.ahbc.com.cn/TenderList.aspx", ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': "省级招标"}),
     f2],
    ["gcjs_zhaobiao_diqu2_gg", "http://www.ahbc.com.cn/CCTenderList.aspx", ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': "市县招标"}),
     f2],
    ["gcjs_biangeng_gg", "http://www.ahbc.com.cn/changeNotice.aspx", ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.ahbc.com.cn/ContractAward.aspx", ["name", "ggstart_time", "href", "info"], f1, f2],

]


# pprint(data)


##安徽招标咨询网
def work(conp, **args):
    est_meta_large(conp, data=data, diqu="安徽省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "anhui"], total=2, headless=True, num=1)
    pass
    # driver=webdriver.Chrome()
    # f=f3(driver,'http://www.ahbc.com.cn/TenderInfo.aspx?clientin=5C76BE4B94BBE00C')
    # print(f)
