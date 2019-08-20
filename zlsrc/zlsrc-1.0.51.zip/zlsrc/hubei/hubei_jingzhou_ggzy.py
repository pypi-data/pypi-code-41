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
from zlsrc.util.etl import est_tbs, est_meta, est_html,  add_info



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="con-list"]//tr[@height="24"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('Paging=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=Paging=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//div[@class="con-list"]//tr[@height="24"][1]//a').get_attribute('href')[-40:-20]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="con-list"]//tr[@height="24"][1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='con-list')
    lis = div.find_all('tr',height="24")

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('td',width="80").get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.jzggzy.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="con-list"]//tr[@height="24"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//td[@class="huifont"]').text
        total = re.findall('/(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//td[@id="tdTitle"][string-length()>5]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//td[@width]/table[@width="100%"][string-length()>100]')
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

    div = soup.find('table',width="998")

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_fangjianshizhen_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006001/006001001/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房建市政'}), f2],
    ["gcjs_gqita_da_bian_fangjianshizhen_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006001/006001002/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房建市政'}), f2],
    ["gcjs_zhongbiaohx_fangjianshizhen_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006001/006001003/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房建市政'}), f2],
    ["gcjs_zhongbiao_fangjianshizhen_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006001/006001004/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房建市政'}), f2],

    ["zfcg_zhaobiao_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002005/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_jiaotong_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006003/006003001/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'交通工程'}), f2],
    ["gcjs_gqita_da_bian_jiaotong_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006003/006003002/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'交通工程'}), f2],
    ["gcjs_zhongbiaohx_jiaotong_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006003/006003003/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'交通工程'}), f2],
    ["gcjs_zhongbiao_jiaotong_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006003/006003004/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'交通工程'}), f2],

    ["gcjs_zhaobiao_shuili_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006005/006005001/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利工程'}), f2],
    ["gcjs_gqita_da_bian_shuili_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006005/006005002/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利工程'}), f2],
    ["gcjs_zhongbiaohx_shuili_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006005/006005003/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利工程'}), f2],
    ["gcjs_zhongbiao_shuili_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006005/006005004/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利工程'}), f2],

    ["gcjs_zhaobiao_shixian_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006008/006008001/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'市县信息'}), f2],
    ["gcjs_gqita_da_bian_shixian_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006008/006008002/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'市县信息'}), f2],
    ["gcjs_zhongbiaohx_shixian_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006008/006008003/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'市县信息'}), f2],
    ["gcjs_zhongbiao_shixian_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006008/006008004/?Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'市县信息'}), f2],

    ["jqita_zhaobiao_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006009/006009001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_da_bian_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006009/006009002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiaohx_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006009/006009003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiao_gg", "http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006009/006009004/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省荆州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_jingzhou"], total=2, headless=True, num=1)



