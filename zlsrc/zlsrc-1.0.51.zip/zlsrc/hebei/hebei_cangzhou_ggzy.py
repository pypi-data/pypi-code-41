import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import est_tbs, est_meta, est_html



def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="ul_list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=page=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//ul[@class="ul_list"]/li[1]/a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//ul[@class="ul_list"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='ul_list')
    lis = div.find_all('li')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('span').get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://xzsp.cangzhou.gov.cn/HBSC/Services/zwfwzx/' + href


        tmp = [name, ggstart_time, href]


        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="ul_list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//div[@class="page"]//a[last()]').get_attribute('href')
        total = re.findall('page=(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="content"][string-length()>10]')
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

    div = soup.find('div', class_='liot')


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://xzsp.cangzhou.gov.cn/HBSC/Services/zwfwzx/a_list.jsp?key=018001001&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://xzsp.cangzhou.gov.cn/HBSC/Services/zwfwzx/a_list.jsp?key=018001004&page=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://xzsp.cangzhou.gov.cn/HBSC/Services/zwfwzx/a_list.jsp?key=018002001&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://xzsp.cangzhou.gov.cn/HBSC/Services/zwfwzx/a_list.jsp?key=018002005&page=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhongbiao_1_gg", "http://xzsp.cangzhou.gov.cn/HBSC/Services/zwfwzx/a_list.jsp?key=018007001&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qsy_zhongbiao_2_gg", "http://xzsp.cangzhou.gov.cn/HBSC/Services/zwfwzx/a_list.jsp?key=018007002&page=1",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省沧州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "cangzhou"], total=2, headless=True, num=1)



