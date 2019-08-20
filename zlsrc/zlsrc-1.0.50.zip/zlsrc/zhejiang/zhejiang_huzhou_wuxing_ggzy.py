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
    locator = (By.XPATH, '//div[@id="ajaxpage-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//div[@id="pages"]/font/font')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//div[@id="pages"]/span').text

    if int(cnum) != int(num):
        val = driver.find_element_by_xpath('//div[@id="ajaxpage-list"]/li[1]/a').get_attribute('href')[
              -30:]
        driver.execute_script('ajaxGoPage(%s)' % num)

        # 第二个等待
        locator = (By.XPATH, '//div[@id="ajaxpage-list"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, '//div[@id="pages"]/font/font')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', id='ajaxpage-list')
    lis = div.find_all('a')

    for tr in lis:
        href=tr['href']
        name=tr['title']
        ggstart_time=tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.wuxing.gov.cn' + href

        tmp = [name, ggstart_time, href]


        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="ajaxpage-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@id="pages"]/font/font')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = re.findall('共(\d+)页', driver.page_source)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="zw"][string-length()>30]')
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

    div = soup.find('div', class_='zw').parent

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_fangjian_gg", "http://ggzy.wuxing.gov.cn/jyxx/fjsz/zbgg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"房建市政"}), f2],
    ["gcjs_gqita_da_bian_fangjian_gg", "http://ggzy.wuxing.gov.cn/jyxx/fjsz/dycq/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"房建市政"}), f2],
    ["gcjs_biangeng_fangjian_gg", "http://ggzy.wuxing.gov.cn/jyxx/fjsz/bggg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"房建市政"}), f2],
    ["gcjs_zhongbiaohx_fangjian_gg", "http://ggzy.wuxing.gov.cn/jyxx/fjsz/pbjggs/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"房建市政"}), f2],
    ["gcjs_zhongbiao_fangjian_gg", "http://ggzy.wuxing.gov.cn/jyxx/fjsz/zbjggg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"房建市政"}), f2],
    ["gcjs_kongzhijia_fangjian_gg", "http://ggzy.wuxing.gov.cn/jyxx/fjsz/kzjtz/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"房建市政"}), f2],

    ["gcjs_zhaobiao_jiaotong_gg", "http://ggzy.wuxing.gov.cn/jyxx/jtgc/zbgg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],
    ["gcjs_gqita_da_bian_jiaotong_gg", "http://ggzy.wuxing.gov.cn/jyxx/jtgc/dycq/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],
    ["gcjs_biangeng_jiaotong_gg", "http://ggzy.wuxing.gov.cn/jyxx/jtgc/bggg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],
    ["gcjs_zhongbiaohx_jiaotong_gg", "http://ggzy.wuxing.gov.cn/jyxx/jtgc/pbjggs/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],
    ["gcjs_zhongbiao_jiaotong_gg", "http://ggzy.wuxing.gov.cn/jyxx/jtgc/zbjggg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],
    ["gcjs_kongzhijia_jiaotong_gg", "http://ggzy.wuxing.gov.cn/jyxx/jtgc/kzjtz/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],

     ["gcjs_zhaobiao_shuili_gg", "http://ggzy.wuxing.gov.cn/jyxx/slgc/zbgg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],
    ["gcjs_gqita_da_bian_shuili_gg", "http://ggzy.wuxing.gov.cn/jyxx/slgc/dycq/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],
    ["gcjs_biangeng_shuili_gg", "http://ggzy.wuxing.gov.cn/jyxx/slgc/bggg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],
    ["gcjs_zhongbiaohx_shuili_gg", "http://ggzy.wuxing.gov.cn/jyxx/slgc/pbjggs/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],
    ["gcjs_zhongbiao_shuili_gg", "http://ggzy.wuxing.gov.cn/jyxx/slgc/zbjggg/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],
    ["gcjs_kongzhijia_shuili_gg", "http://ggzy.wuxing.gov.cn/jyxx/slgc/kzjtz/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],

    ["zfcg_zhaobiao_gg", "http://ggzy.wuxing.gov.cn/jyxx/zfcg/zbgg/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://ggzy.wuxing.gov.cn/jyxx/zfcg/gzgg/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://ggzy.wuxing.gov.cn/jyxx/zfcg/jggg/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yucai_gg", "http://ggzy.wuxing.gov.cn/jyxx/zfcg/yjzx/index.html",["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_gg", "http://ggzy.wuxing.gov.cn/jyxx/qtjy/index.html",["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省湖州市吴兴区", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "wuxing"], total=2, headless=True, num=1)



