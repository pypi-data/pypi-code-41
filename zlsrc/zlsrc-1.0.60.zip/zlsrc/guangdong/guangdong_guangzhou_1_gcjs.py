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
from zlsrc.util.etl import  est_html,  add_info, est_meta_large



def f1(driver, num):
    locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[2]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum=re.findall('pager.offset=(\d+)&',url)[0]
    cnum=int(cnum)/10+1

    if int(cnum) != int(num):

        url=re.sub('(?<=pager.offset=)\d+',str((num-1)*10),url)


        val = driver.find_element_by_xpath('//table[@class="wsbs-table"]//tr[3]//a').get_attribute('href')[-50:-20]

        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[3]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='wsbs-table')
    lis = div.find_all('tr')[1:]

    for tr in lis:
        tds=tr.find_all('td')
        pro_index=tds[1].get_text()
        name=tds[2].get_text()
        href=tds[2].a['href']
        pname=tds[3].get_text()
        ggstart_time=tds[4].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://113.108.174.135' + href
        info=json.dumps({'pro_index':pro_index,'pname':pname},ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[2]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//div[@class="pagination page-mar"]/ul/span[last()]').text
        total = re.findall('共(\d+)页', page)[0]
        total = int(total)
    except:
        total=1


    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="sbox"][string-length()>60] | //div[@id="main-content"]')
    WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator))

    if "113.108.174.135" in driver.title and "找不到与以下网址对应的网" in driver.page_source:
        return "404"

    locator = (By.XPATH, '//div[@class="sbox"][string-length()>60]')
    WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator))

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

    div = soup.find('div', class_='bigbox')

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["xm_beian_wenjian_gg", "http://113.108.174.135/cms/bbwz/layout2/XmListServlet?channelId=17&xmmc=&zbbh=&pager.offset=0&flag=jw",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':"招标文件备案"}), f2],
    ["xm_beian_qingkuang_gg", "http://113.108.174.135/cms/bbwz/layout2/XmListServlet?channelId=18&xmmc=&zbbh=&pager.offset=0&flag=jw",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':"招标情况备案"}), f2],


]



###广州市建设工程招投标监督管理综合平台
def work(conp, **args):
    est_meta_large(conp, data=data, diqu="广东省广州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "guangdong_guangzhou"], total=3, headless=False, num=1)
    driver=webdriver.Chrome()
    url='http://113.108.174.135/cms/bbwz/layout3/xmdetail_jw.jsp?siteId=1&id=16ce16ce-13459f2c7fb-b5c3d07dc51290ee0c21d14e84efc219'
    f=f3(driver,url)
    print(f)


