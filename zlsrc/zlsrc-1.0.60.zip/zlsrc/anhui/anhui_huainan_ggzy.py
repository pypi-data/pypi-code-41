from pprint import pprint
from collections import OrderedDict

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
from zlsrc.util.etl import  est_meta, est_html,  add_info



def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('Paging=(\d+)',url)[0]
    if int(cnum) != num:
        val=driver.find_element_by_xpath('//ul[@class="ewb-info-items"]/li[1]/a').get_attribute('href')[-50:-20]
        url=re.sub('Paging=\d+','Paging=%d'%num,url)
        driver.get(url)
        locator=(By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('li', class_='ewb-info-item')

    for tr in lis:

        href = tr.a['href']
        name = tr.a['title']
        ggstart_time = tr.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://ggj.huainan.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
        # print(tmp)
    df = pd.DataFrame(data=data)

    df["info"] = None
    return df


def f2(driver):
    locator=(By.XPATH,'//ul[@class="ewb-info-items"]/li[1]/a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//td[@class="huifont"]').text
    total=re.findall('/(\d+)',total)[0]
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[contains(@id,"menutab") and (not(@style) or @style="")] | //div[@id="mainContent"] | //div[@class="ewb-article-info"][string-length()>100]')

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

    div=soup.find('div',id="mainContent").parent
    if div == None:
        div = soup.find('div', attrs={'id': re.compile('menutab_[45]_\d'), 'style': ''})
        if div == None:
            div=soup.find('div',class_='ewb-article-info').parent

    return div




def get_data():
    data = []

    #gcjs
    ggtype1 = OrderedDict([("zhaobiao","001"),("gqita_da_bian", "003"), ("zhongbiaohx", "004"),("zhongbiao","002")])
    #zfcg
    ggtype2 = OrderedDict([("zhaobiao","001"),("dyly","006"),("gqita_da_bian", "005"), ("zhongbiao", "002")])

    ##zfcg_gcjs
    adtype1 = OrderedDict([('市本级','001'),("寿县", "002"), ("凤台县", "003")])

    #gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://ggj.huainan.gov.cn/HNWeb_NEW/jyxx/002001/002001{jy}/002001{jy}{dq}/?Paging=1".format(dq=adtype1[w2],jy=ggtype1[w1])
            tmp = ["gcjs_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href = "http://ggj.huainan.gov.cn/HNWeb_NEW/jyxx/002002/002002{jy}/002002{jy}{dq}/?Paging=1".format(dq=adtype1[w2],jy=ggtype2[w1])
            tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    data1 = data.copy()

    data1.append(["gcjs_gqita_xiao_gg", "http://ggj.huainan.gov.cn/HNWeb_NEW/jyxx/002001/002001005/002001005002/?Paging=1",
                  ["name", "ggstart_time", "href", 'info'], add_info(f1, {"diqu":"寿县"}), f2], )
    return data1

data=get_data()
# pprint(data)


###淮南市公共资源交易中心
def work(conp,**args):
    est_meta(conp,data=data,diqu="安徽省淮南市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    work(conp=["postgres", "since2015", "192.168.3.171", "anhui", "huainan"])
    pass

