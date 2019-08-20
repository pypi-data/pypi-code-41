import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zlsrc.util.etl import est_tbs,est_meta,est_html


def f1(driver,num):
    locator = (By.XPATH, '//*[@id="rightout"]/div[1]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=url.rsplit('/', maxsplit=1)[1].split('.')[0]


    if str(num) !=cnum:
        url = url.rsplit('/', maxsplit=1)[0] + '/' + '{}.html'.format(num)

        val = driver.find_element_by_xpath('//*[@id="rightout"]/div[1]/ul/li[1]/a').get_attribute('href')[-30:-5]
        driver.get(url)
        locator = (By.XPATH, "//*[@id='rightout']/div[1]/ul/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    uls = soup.find('div', class_='menu-list')
    lis = uls.find_all('li')
    for li in lis:

        href = li.a['href'].strip('.')
        name = li.a.get_text().strip()
        ggstart_time = li.span.get_text().strip()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.jdz.gov.cn' + href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="rightout"]/div[1]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//*[@id="index"]').text
    total = int(page.strip().split('/')[1])
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//td[@id="content"][string-length()>50] | //div[@class="article"][string-length()>50]')

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
    div = soup.find('td',id="content")
    if div == None:
        div=soup.find('div',class_="article")
    return div

data=[
    #
    ["gcjs_zhaobiao_gg","http://www.jdz.gov.cn/xxgk/050014/050014004/1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://www.jdz.gov.cn/xxgk/050014/050014005/1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_zhao_zhong_gg","http://www.jdz.gov.cn/xxgk/050014/050014003/1.html",["name","ggstart_time","href",'info'],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省景德镇市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':


    conp=["postgres","since2015","192.168.3.171","jiangxi","jingdezhen"]

    work(conp=conp,headless=False,num=1)