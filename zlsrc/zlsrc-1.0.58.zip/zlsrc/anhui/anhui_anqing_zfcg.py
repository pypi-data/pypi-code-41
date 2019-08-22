import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import est_meta, est_html


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="list-tab"]/tbody/tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum=re.findall('page=(\d+)',url)[0]

    if str(cnum) != str(num):
        url=re.sub('(?<=page=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//table[@class="list-tab"]/tbody/tr[2]//a').get_attribute('href')[-15:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//table[@class="list-tab"]/tbody/tr[2]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='list-tab').tbody
    lis = div.find_all('tr',recursive=False)[1:]

    for tr in lis:
        name=tr.find('a').get_text()
        href=tr.find('a')['href']
        tds=tr.find_all('td',recursive=False)
        pro_code=tds[-2].get_text()
        ggstart_time=tds[-1].get_text().strip('[').strip(']')
        info = json.dumps({"pro_code":pro_code}, ensure_ascii=False)
        href='http://aqxxgk.anqing.gov.cn//'+href
        tmp = [name, ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="list-tab"]/tbody/tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.find_element_by_link_text('最后一页').get_attribute('href')


    total = re.findall('page=(\d+)', page)[0]
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="page_c content_c"][string-length()>100]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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

    div = soup.find('div', class_='page_c content_c')

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["zfcg_zhaobiao_gg", "http://aqxxgk.anqing.gov.cn//all_list.php?xxflid=171102&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://aqxxgk.anqing.gov.cn//all_list.php?xxflid=171103&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
]


##安庆市政府信息公开网
def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省安庆市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anhui", "anhui_anqing_zfcg"],num=1)



