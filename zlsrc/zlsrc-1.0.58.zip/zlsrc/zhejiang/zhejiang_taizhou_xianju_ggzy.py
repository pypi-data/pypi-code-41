import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="roundin"]/table[2]//tr[2]//table[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('pageindex=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=pageindex=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//div[@class="roundin"]/table[2]//tr[2]//table[1]//a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="roundin"]/table[2]//tr[2]//table[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='roundin').find_all('table',recursive=False)[1]
    lis = div.find_all('table')[:-1]

    for tr in lis:
        href=tr.find('a')['href'].strip('..')
        name=tr.find('a').get_text(strip=True)
        ggstart_time=tr.find('td',width="102").get_text().strip('[').strip(']')
        if 'http' in href:
            href = href
        else:
            href = 'http://xjztb.cn' + href


        tmp = [name, ggstart_time, href]


        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="roundin"]/table[2]//tr[2]//table[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//select[@name="fey"]/option[last()]').text
        total = int(page)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@id="Table2"][string-length()>100]')
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

    div = soup.find('table',id="Table2")


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=11&pageindex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=12&pageindex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=15&pageindex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=13&pageindex=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_jizhong_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=28&pageindex=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'cgfs':"集中采购"}), f2],
    ["zfcg_zhaobiao_jizhong_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=21&pageindex=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'cgfs':"集中采购"}), f2],
    ["zfcg_zhongbiao_jizhong_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=22&pageindex=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'cgfs':"集中采购"}), f2],

    ["zfcg_yucai_fensan_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=63&pageindex=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'cgfs':"分散采购"}), f2],
    ["zfcg_zhaobiao_fensan_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=61&pageindex=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'cgfs':"分散采购"}), f2],
    ["zfcg_zhongbiao_fensan_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=62&pageindex=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'cgfs':"分散采购"}), f2],

    ["jqita_zhaobiao_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=51&pageindex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiao_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=52&pageindex=1",["name", "ggstart_time", "href", "info"],f1, f2],
    ["jqita_gqita_bian_da_gg", "http://xjztb.cn/Bulletin/viewmore1.aspx?BulletinTypeId=53&pageindex=1",["name", "ggstart_time", "href", "info"],f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省台州市仙居县", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "xinajuxian"], total=2, headless=True, num=1)



