import json


import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zlsrc.util.etl import  est_meta, est_html, add_info, est_gg



def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a | //ul[@class="ewb-public-items"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    try:
        cnum=driver.find_element_by_xpath('//li[@class="ewb-page-li page first current"]').text
    except:
        cnum=1

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//ul[@class="wb-data-item"]/li[1]//a | //ul[@class="ewb-public-items"]/li[1]//a').get_attribute('href')[-30:]
        # print(val)

        mark=re.findall('/(\d+?)/$',url)[0]
        driver.execute_script("ShowAjaxNewPage('categorypagingcontent','/zgbp/','%s',%s)"%(mark,num))

        locator = (
            By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a[not(contains(@href,"{val}"))] | //ul[@class="ewb-public-items"]/li[1]//a[not(contains(@href,"{val}"))]'.format(val=val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", class_=['wb-data-item','ewb-public-items'])
    dls = div.find_all("li")
    data = []
    for dl in dls:

        href=dl.find('a')['href']
        name=dl.find('a').get_text(strip=True)

        ggstart_time = dl.find('span').get_text()

        href='http://www.bp.gov.cn'+href

        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a | //ul[@class="ewb-public-items"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total=driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-noborder ewb-page-num"]').text
        total=re.findall('\d/(\d+)',total)[0]
    except:
        total=1
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="mainContent"][string-length()>100]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', id='mainContent').parent

    return div



data=[

["gcjs_zhaobiao_gg" , 'http://www.bp.gov.cn/zgbp/ggzy/007001/007001001/', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiaohx_gg" , 'http://www.bp.gov.cn/zgbp/ggzy/007001/007001002/', ["name", "ggstart_time", "href", 'info'],f1, f2],

["zfcg_zhaobiao_gg" , 'http://www.bp.gov.cn/zgbp/ggzy/007002/007002001/', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhongbiao_gg" , 'http://www.bp.gov.cn/zgbp/ggzy/007002/007002002/', ["name", "ggstart_time", "href", 'info'],f1, f2],


      ]


###北票市人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="辽宁省朝阳市北票市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=False,
        num=1,
        )
    pass