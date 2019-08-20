import time
from collections import OrderedDict
from os.path import dirname, join
from pprint import pprint

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zlsrc.util.etl import est_tbs, est_meta, est_html,  add_info



def f1(driver,num):

    locator = (By.XPATH, '//ul[@class="ewb-com-items"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('pageing=(\d+)',url)[0]
    if int(cnum) != num:
        val=driver.find_element_by_xpath('//ul[@class="ewb-com-items"]/li[1]//a').get_attribute('href')[-50:-20]
        url=re.sub('pageing=\d+','pageing=%d'%num,url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="ewb-com-items"]/li[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='ewb-com-items')
    trs = div.find_all('li')

    for tr in trs:
        href = tr.div.a['href']
        name = tr.div.a.get_text().strip()
        ggstart_time = tr.span.get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.jlsggzyjy.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator=(By.XPATH,'//ul[@class="ewb-com-items"]/li[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    try:
        total=driver.find_element_by_xpath('//li[@class="wb-page-li"][last()-1]/a').text
        total=re.findall('/(\d+)',total)[0]
    except:
        total=1
    return int(total)




def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-container ewb-mt10"]')

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
    div = soup.find('div',class_='ewb-mt10')
    return div


def get_data():
    data = []

    #gcjs
    ggtype1 = OrderedDict([("zhaobiao","001"),("biangeng", "002"), ("zhongbiaohx", "003")])
    #zfcg
    ggtype2 = OrderedDict([("zhaobiao","001"),("biangeng","002"),("zhongbiaohx", "003")])

    ##zfcg_gcjs
    adtype1 = OrderedDict([('吉林市','001'),('永吉县','002'),('磐石市','004')])


    #gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://www.jlsggzyjy.gov.cn/jlsztb/jyxx/003001/003001{jy}/003001{jy}{dq}/?pageing=1".format(dq=adtype1[w2],jy=ggtype1[w1])
            tmp = ["gcjs_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    #zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href = "http://www.jlsggzyjy.gov.cn/jlsztb/jyxx/003002/003002{jy}/003002{jy}{dq}/?pageing=1".format(dq=adtype1[w2],jy=ggtype2[w1])
            tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    remove_arr = ["gcjs_biangeng_diqu002_gg","gcjs_zhongbiaohx_diqu002_gg"]
    data1 = data.copy()
    for w in data:
        if w[0] in remove_arr: data1.remove(w)

    href='http://www.jlsggzyjy.gov.cn/jlsztb/jyxx/003001/003001004/003001004001/?pageing=1'
    data1.append(['gcjs_zhongbiao_diqu001_gg',href,["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": "吉林市"}), f2])
    return data1

data=get_data()

# pprint(data)



def work(conp,**args):
    est_meta(conp,data=data,diqu="吉林省吉林市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':


    driver =webdriver.Chrome()
    print(f3(driver, 'http://www.jlsggzyjy.gov.cn/jlsztb/InfoDetail/?InfoID=aec93abf-109e-41fb-a851-d99c4831644a&CategoryNum=008006'))
    # work(conp=["postgres","since2015","192.168.3.171","jilin","jilinshi"])
    pass