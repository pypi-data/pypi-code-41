import time
from collections import OrderedDict
from os.path import dirname, join
from pprint import pprint

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zlsrc.util.etl import  est_meta, est_html, add_info




def f1(driver, num):

    locator = (By.XPATH, '(//td[@class="ewb-project-td"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    if 'projectlist.html' in url:
        cnum=1
    else:
        cnum=re.findall('/(\d+).html',url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('(//td[@class="ewb-project-td"])[1]/a').get_attribute(
            "href")[- 30:-5]

        if num == 1:
            url=re.sub('/\d+.html','/projectlist.html',url)
        else:
            url=re.sub('(?<=/)[projectlist\d]*?(?=.html)',str(num),url)


        driver.get(url)

        locator = (By.XPATH, '(//td[@class="ewb-project-td"])[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data_ = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('table',class_='ewb-project-tb table').find('tbody').find_all('tr',recursive=False)

    for tr in trs:
        href = tr.find('a')['href']
        name = tr.find('a')['title']

        ggstart_time = tr.find_all('td')[-1].get_text(strip=True)

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjy.xuancheng.gov.cn' + href

        tmp = [name, ggstart_time, href]
        # print(tmp)
        data_.append(tmp)
    df = pd.DataFrame(data=data_)
    df["info"] = None
    return df


def f2(driver):
    url=driver.current_url
    locator = (By.XPATH, '(//td[@class="ewb-project-td"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    mark = re.findall('/(\d+)(?=/projectlist.html)', url)[0]
    url=re.sub('/\d+/projectlist.html','/projectBuild.html',url)
    driver.get(url)
    time.sleep(0.5)
    WebDriverWait(driver,10).until(lambda driver:'projectlist' not in driver.current_url)

    locator = (By.XPATH, '(//td[@class="ewb-project-td"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total = driver.find_element_by_xpath('//div[@id="page%s"]/ul/li[last()]/a'%mark).get_attribute('data-page-index')
    except:
        total=1

    driver.quit()

    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="tab-view"]//div[contains(@data-role,"tab-content") and (not(@class) or @class="")][string-length()>50] |//div[@id="nr"]/div[@class="detail-body news_content"][string-length()>100]|//div[@class="ewb-list-main"]')

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

    div=soup.find('div',id="nr")
    if not div:
        div = soup.find('div',class_='ewb-list-main')
    return div

def get_data():
    data = []

    ##gcjs
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("gqita_da_bian","002"),("zhongbiaohx", "003"), ("zhongbiao", "004")])

    ##zfcg
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("yucai", "002"),("gqita_da_bian","003"), ("zhongbiao", "004")])
    ##shehuicaigou
    ggtype3 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"),("gqita_da_bian","003"), ("zhongbiao", "004")])

    adtype1 = OrderedDict([('本级','1'),("宣州", "2"), ("郎溪", "3"), ("广德", "4"), ("宁国", "5"),
                          ('泾县','6'),('绩溪','7'),('旌德','8')])

    ##gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href="http://ggzyjy.xuancheng.gov.cn/xcspfront/jsgc/01600{0}/01600{1}{2}/projectlist.html".format(adtype1[w2],adtype1[w2],ggtype1[w1])
            tmp=["gcjs_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    ##zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href="http://ggzyjy.xuancheng.gov.cn/xcspfront/zfcg/01700{0}/01700{1}{2}/projectlist.html".format(adtype1[w2],adtype1[w2],ggtype2[w1])
            tmp=["zfcg_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    ##shehuicaigou
    for w1 in ggtype3.keys():
        for w2 in adtype1.keys():
            href="http://ggzyjy.xuancheng.gov.cn/xcspfront/shcgxm/02200{0}/02200{1}{2}/projectlist.html".format(adtype1[w2],adtype1[w2],ggtype3[w1])
            tmp=["qsy_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2,"gclx":"社会采购"}),f2]
            data.append(tmp)

    ##xiane
    for w1 in ggtype3.keys():
        for w2 in adtype1.keys():
            href="http://ggzyjy.xuancheng.gov.cn/xcspfront/xeyxxm/02100{0}/02100{1}{2}/projectlist.html".format(adtype1[w2],adtype1[w2],ggtype3[w1])
            tmp=["jqita_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2,"gclx":"限额以下项目"}),f2]
            data.append(tmp)

    r_list=['zfcg_yucai_diqu2_gg','jqita_biangeng_diqu3_gg','jqita_biangeng_diqu4_gg',
            'jqita_biangeng_diqu8_gg','qsy_gqita_da_bian_diqu1_gg','qsy_gqita_da_bian_diqu2_gg',
            'qsy_biangeng_diqu2_gg','qsy_zhongbiao_diqu2_gg','qsy_zhaobiao_diqu2_gg','qsy_gqita_da_bian_diqu3_gg',
            'qsy_biangeng_diqu3_gg','qsy_gqita_da_bian_diqu4_gg','qsy_biangeng_diqu4_gg',
            'qsy_biangeng_diqu5_gg','qsy_gqita_da_bian_diqu5_gg','qsy_zhongbiao_diqu5_gg','qsy_zhaobiao_diqu5_gg',
            'qsy_gqita_da_bian_diqu6_gg','qsy_biangeng_diqu6_gg','qsy_gqita_da_bian_diqu7_gg','qsy_biangeng_diqu7_gg',
            'qsy_gqita_da_bian_diqu8_gg','qsy_biangeng_diqu8_gg']

    data1 = data.copy()
    for w in data1:
        if w[0] in r_list:data1.remove(w)

    return data1

data = get_data()

# pprint(data)

##域名变更:http://ggzyjy.xuancheng.gov.cn
##变更日期: 2019-07-15


def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省宣城市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anhui", "xuancheng"],num=1,headless=True,ipNum=0)

    pass
    # driver=webdriver.Chrome()
    # print(f3(driver, 'http://ggzyjy.xuancheng.gov.cn/xcspfront/jsgc/016001/016001001/20190812/5f657096-fe70-4f8f-ba89-4eae78b0b6a3.html'))
    # print(f)

