import time
from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zlsrc.util.etl import  est_meta, est_html, add_info


def f1(driver,num):

    locator = (By.XPATH, '//ul[@class="ewb-lbd-items"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = url.rsplit('=', maxsplit=1)[1]
    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@class="ewb-lbd-items"]/li[1]/a').get_attribute('href')[-50:-25]

        url = re.sub('Paging=\d+', 'Paging=%s' % num, url)

        driver.get(url)

        locator = (By.XPATH, '//ul[@class="ewb-lbd-items"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='ewb-lbd-items')
    trs = div.find_all('li')

    for tr in trs:
        href = tr.a['href']
        name = tr.a['title']
        ggstart_time = tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.szggzyjy.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df['info']=None
    return df




def f2(driver):
    locator = (By.XPATH, '//ul[@class="ewb-lbd-items"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//td[@class="huifont"]').text
    total=re.findall('/(\d+)',total)[0]
    total = int(total)
    driver.quit()
    return total



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, ' //div[contains(@id,"menutab") and (not(@style) or @style="")] | //div[@id="mainContent"]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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

    div = soup.find('div', id='mainContent').parent

    if div == None:
        div = soup.find('div', attrs={'id': re.compile('menutab_[45]_\d'), 'style': ''})
        if div == None:
            raise ValueError('div is None')
    return div



def get_data():
    data = []

    #gcjs
    ggtype1 = OrderedDict([("zhaobiao","001"),("gqita_da_bian", "002"), ("zhongbiaohx", "003"),("zhongbiao","004"),("liubiao","006")])
    #zfcg
    ggtype2 = OrderedDict([("yucai","001"),("zhaobiao","002"),("gqita_da_bian", "003"), ("zhongbiao", "004"),("liubiao","006")])

    ##zfcg_gcjs
    adtype1 = OrderedDict([('宿州市','1'),("埇桥区", "2"), ("砀山县", "3"), ("萧县", "4"), ("灵璧县", "5"),("泗县","6")])

    #gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://www.szggzyjy.cn/szfront/jyxx/002001/002001{jy}/002001{jy}00{dq}/?Paging=1".format(dq=adtype1[w2],jy=ggtype1[w1])
            tmp = ["gcjs_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    #zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href = "http://www.szggzyjy.cn/szfront/jyxx/002002/002002{jy}/002002{jy}00{dq}/?Paging=1".format(dq=adtype1[w2],jy=ggtype2[w1])
            tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)


    data1 = data.copy()

    data2=[
    ["jqita_zhaobiao_gg", "http://www.szggzyjy.cn/szfront/jyxx/002005/002005001/?Paging=1",["name", "ggstart_time", "href", 'info'], f1, f2],
    ["jqita_zhongbiao_gg", "http://www.szggzyjy.cn/szfront/jyxx/002005/002005002/?Paging=1",["name", "ggstart_time", "href", 'info'], f1, f2],
    ["jqita_gqita_da_bian_gg", "http://www.szggzyjy.cn/szfront/jyxx/002005/002005003/?Paging=1",["name", "ggstart_time", "href", 'info'], f1, f2],
    ["qsy_zhaobiao_gg", "http://www.szggzyjy.cn/szfront/jyxx/002006/002006001/?Paging=1",["name", "ggstart_time", "href", 'info'], f1, f2],
    ["qsy_zhongbiao_gg", "http://www.szggzyjy.cn/szfront/jyxx/002006/002006002/?Paging=1",["name", "ggstart_time", "href", 'info'], f1, f2],
    ["qsy_gqita_da_bian_gg", "http://www.szggzyjy.cn/szfront/jyxx/002006/002006003/?Paging=1",["name", "ggstart_time", "href", 'info'], f1, f2],

           ]
    data1.extend(data2)
    return data1

data=get_data()
# pprint(data)


def work(conp,**args):
    est_meta(conp,data=data,diqu="安徽省宿州市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':

    conp = ["postgres", "since2015", "192.168.4.198", "anhui", "anhui_suzhou_ggzy"]

    # work(conp=conp)
    pass
