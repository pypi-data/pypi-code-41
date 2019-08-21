import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info



def f1(driver, num):
    locator = (By.XPATH, '//table[contains(@id, "ctl00_ContentPlaceHolder")]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        cnum=int(driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_T2"]').get_attribute('value'))
    except:
        cnum = int(driver.find_element_by_xpath('//span[@id="ctl00_ContentPlaceHolder2_lblCurrentIndex"]').text.strip())

    if int(cnum) != int(num):
        while True:
            try:
                cnum = int(driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_T2"]').get_attribute('value'))
            except:
                cnum = int(driver.find_element_by_xpath('//span[@id="ctl00_ContentPlaceHolder2_lblCurrentIndex"]').text.strip())
            val = driver.find_element_by_xpath('//table[contains(@id, "ctl00_ContentPlaceHolder")]/tbody/tr[1]//a').get_attribute('href')[-45:]

            if cnum > num:
                if cnum - num > page_total//2:
                    first_b=driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_F1"]')
                    driver.execute_script("arguments[0].click()", first_b)
                else:
                    pre_b = driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_F2"]')
                    driver.execute_script("arguments[0].click()", pre_b)

            elif cnum < num :
                if num - cnum > page_total//2:
                    last_b = driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_F4"]')
                    driver.execute_script("arguments[0].click()", last_b)
                else:
                    nex_b = driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_F3"]')
                    driver.execute_script("arguments[0].click()", nex_b)

            else:
                break

            # 第二个等待
            locator = (By.XPATH, '//table[contains(@id, "ctl00_ContentPlaceHolder")]/tbody/tr[1]//a[not(contains(@href,"{}"))]'.format(val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table',id=re.compile('ctl00_ContentPlaceHolder')).find('tbody').find_all('tr',recursive=False)

    for tr in div:

        href=tr.find('a')['href']
        name=tr.find('a').get_text(strip=True)

        ggstart_time=tr.find_all('nobr')[-1].get_text()

        if 'http' in href:
            href=href
        else:
            href='http://ggzyjy.cqjb.gov.cn/lbv3/'+href

        tmp = [name, ggstart_time, href]
        data.append(tmp)

    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    global page_total
    locator = (By.XPATH, '//table[contains(@id, "ctl00_ContentPlaceHolder")]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        page_total = int(driver.find_element_by_xpath('//input[@id="ctl00_ContentPlaceHolder2_T1"]').get_attribute('value'))
    except:
        page_total=int(driver.find_element_by_xpath('//span[@id="ctl00_ContentPlaceHolder2_A1"] | //span[@id="ctl00_ContentPlaceHolder2_lblPageCount"]').text)


    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@bgcolor="#FFFFFF"][string-length()>200]')
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

    div = soup.find('table',bgcolor="#FFFFFF")

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_zb_item.aspx?ILWHBNjF4ckRKalAUGeb6A==",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA==",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_item.aspx?ILWHBNjF4cmO4mGagitSfg==",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_zb_item.aspx?ILWHBNjF4cnK/zAZkqtxEQ==",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiaohx_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_zz_item.aspx?ILWHBNjF4cnt57FZxA1uhw==",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_zz_item.aspx?ILWHBNjF4cloJjmrFB4k4Q==",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_da_bian_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_item.aspx?ILWHBNjF4cnfR2eoE5NhGQ==",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_dyly_1_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_zb_item.aspx?ILWHBNjF4cnKxu5TEUPunw==",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_dyly_2_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_zz_item.aspx?ILWHBNjF4cn6Dx+w126yEQ==",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_fenshan_gg", "http://ggzyjy.cqjb.gov.cn/lbv3/n_newslist_zb_item.aspx?ILWHBNjF4ckTwEn7BZRdmw==",["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"分散采购"}), f2],

    

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆市江北区", **args)
    est_html(conp, f=f3, **args)



# 修改日期:2019/7/31
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "jiangbei"], total=2, headless=False, num=1)

    #
    # for d in data[2:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 3)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
