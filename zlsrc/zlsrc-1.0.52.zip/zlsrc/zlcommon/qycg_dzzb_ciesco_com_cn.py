import json
import math
import re

import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="zbgg_table"]/table/tbody/tr[child::td]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    if "xjcgList" not in driver.current_url:
        val = driver.find_element_by_xpath('//div[@class="zbgg_table"]/table/tbody/tr[child::td][1]/td/a').get_attribute("href")[-50:]
    else:
        val = driver.find_element_by_xpath('//div[@class="zbgg_table"]/table/tbody/tr[child::td][1]/td/a').get_attribute("onclick")[-30:]
    cnum = driver.find_element_by_xpath('//a[@class="cur-ye"]/span').text
    # print(val,cnum)
    if int(cnum) != int(num):
        driver.execute_script("pagination(%s)" % num)
        locator = (By.XPATH, '//div[@class="zbgg_table"]/table/tbody/tr[child::td][1]/td/a[not(contains(@href,"%s"))]|//div[@class="zbgg_table"]/table/tbody/tr[child::td][1]/td/a[not(contains(@onclick,"%s"))]' % (val,val))
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="zbgg_table"]/table/tbody/tr[child::td]')
    for content in content_list:
        name = content.xpath('./td/a/@title')[0].strip()
        if "xjcg" not in driver.current_url:
            project_code = content.xpath('./td[2]/text()')[0].strip()
            buyer_name = content.xpath('./td[last()-1]/text()')[0].strip()

        else:
            project_code = content.xpath('./td[2]/a/text()')[0].strip()
            buyer_name = content.xpath('./td[last()-1]/a/text()')[0].strip()
        if "xjcgList" not in driver.current_url:
            url = 'https://dzzb.ciesco.com.cn' + content.xpath('./td/a/@href')[0].strip()
        else:
            url = 'https://dzzb.ciesco.com.cn/xjcg/xjcgDetail?guid=' + re.findall('\'([^\']+)\'',content.xpath('./td/a/@onclick')[0].strip())[1]

        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        info = json.dumps({'project_code':project_code,'buyer_name':buyer_name},ensure_ascii=False)
        temp = [name,  ggstart_time, url, info]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="fenye"]/ul/li[last()-1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//div[@class="fenye"]/ul/li[last()-1]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    if 'iframe' in driver.page_source:
        locator = (By.TAG_NAME, 'iframe')
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
        if 'iframepage' in driver.page_source:
            frame = driver.find_element_by_id('iframepage')
            driver.switch_to.frame(frame)
        locator = (By.XPATH, '//div[@class="template"]|//div[@class="page_contect bai_bg"]')
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    else:
        locator = (By.XPATH, '//div[@class="jyxx_qxy"]')
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='template')
    if  not div:
        div = soup.find('div', class_='page_contect bai_bg')
        if not div:
            div = soup.find('div', class_='jyxx_qxy')

    if 'iframe' in driver.page_source:
        driver.switch_to.default_content()

    return div


data = [

    ["qycg_zgys_gg",
     "https://dzzb.ciesco.com.cn/gg/zgysList",
     ["name", "ggstart_time","href", "info"], f1, f2],
    ["qycg_zhaobiao_gg",
     "https://dzzb.ciesco.com.cn/gg/ggList",
     ["name", "ggstart_time","href", "info"], f1, f2],
    ["qycg_biangeng_gg",
     "https://dzzb.ciesco.com.cn/gg/ggbgList",
     ["name", "ggstart_time","href", "info"], f1, f2],

    ["qycg_zhongbiaohx_gg",
     "https://dzzb.ciesco.com.cn/gg/pbjgList",
     ["name", "ggstart_time","href", "info"], f1, f2],
    ["qycg_gqita_dingbiao_gg",
     "https://dzzb.ciesco.com.cn/gg/dbjggsList",
     ["name", "ggstart_time","href", "info"], f1, f2],
    ["qycg_zhongbiao_gg",
     "https://dzzb.ciesco.com.cn/gg/zbgsList",
     ["name", "ggstart_time","href", "info"], f1, f2],
    ["qycg_liubiao_gg",
     "https://dzzb.ciesco.com.cn/gg/zbycList",
     ["name", "ggstart_time","href", "info"], f1, f2],

    ["qycg_zhaobiao_fzb_gg",
     "https://dzzb.ciesco.com.cn/xjcg/xjcgList",
     ["name", "ggstart_time","href", "info"], add_info(f1,{"tag":"非招标"}), f2],
    ["qycg_biangeng_fzb_gg",
     "https://dzzb.ciesco.com.cn/xjcg/bgggList",
     ["name", "ggstart_time","href", "info"], add_info(f1,{"tag":"非招标"}), f2],

    ["qycg_zhongbiao_fzb_gg",
     "https://dzzb.ciesco.com.cn/xjcg/jgggList",
     ["name", "ggstart_time","href", "info"], add_info(f1,{"tag":"非招标"}), f2],
    ["qycg_liubiao_fzb_gg",
     "https://dzzb.ciesco.com.cn/xjcg/ycggList",
     ["name", "ggstart_time","href", "info"], add_info(f1,{"tag":"非招标"}), f2],

]

###招商局集团电子招标采购交易网
def work(conp, **args):
    est_meta(conp, data=data, diqu="招商局集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "dzzb_ciesco_com_cn"]
    # work(conp,pageloadstrategy='none',pageloadtimeout='30')
    # driver = webdriver.Chrome()
    # driver.get("https://dzzb.ciesco.com.cn/gg/zgysList")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    driver = webdriver.Chrome()
    print(f3(driver, 'https://dzzb.ciesco.com.cn/xjcg/bgggDetail?guid=4cbf9851-5e8f-423d-b7d0-5b126c9a0cdf'))
    # driver.close()