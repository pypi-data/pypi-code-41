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
    locator = (By.XPATH, '//ul[@class="article clearfix"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = re.findall('index_(\d+).jhtml',url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//ul[@class="article clearfix"]/li[1]//a').get_attribute('href')[-20:]

        url=re.sub('(?<=index_)\d+',str(num),url)
        # print(url)
        driver.get(url)

        locator = (
            By.XPATH, '//ul[@class="article clearfix"]/li[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", class_="article clearfix")
    dls = div.find_all("li")
    data = []
    for dl in dls:

        href=dl.find('a')['href']
        name=dl.find('a')['title']

        ggstart_time = dl.find('p',class_='release-time').get_text()

        tag=dl.find('p',class_='article-detailed').get_text()
        xiangmu_code=re.findall('项目编号：(.*)建设单位',tag)[0].strip()
        jianshe_dw=re.findall('建设单位：(.*)$',tag)[0].strip()
        info=json.dumps({"xiangmu_code":xiangmu_code,'jianshe_dw':jianshe_dw},ensure_ascii=False)


        tmp = [name, ggstart_time, href,info]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="article clearfix"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//ul[@class="pages-list"]/li[1]/a').text
    total=re.findall('共\d+条记录 \d/(\d+)页',total)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="content2"][string-length()>100]')
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
    div = soup.find('div', class_='content2')

    return div



data=[

["gcjs_zhaobiao_gg" , 'http://www.bjhd.gov.cn/ggzyjy/gcjsFjgc/index_1.jhtml', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiaohx_gg" , 'http://www.bjhd.gov.cn/ggzyjy/gcjsSzgc/index_1.jhtml', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiao_gg" , 'http://www.bjhd.gov.cn/ggzyjy/gcjsSwgc/index_1.jhtml', ["name", "ggstart_time", "href", 'info'],f1, f2],

["zfcg_yucai_gg" , 'http://www.bjhd.gov.cn/ggzyjy/zfcgBqgs/index_1.jhtml', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhaobiao_gg" , 'http://www.bjhd.gov.cn/ggzyjy/zfcgZbgg/index_1.jhtml', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_biangeng_gg" , 'http://www.bjhd.gov.cn/ggzyjy/zfcgXxgzgs/index_1.jhtml', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhongbiao_gg" , 'http://www.bjhd.gov.cn/ggzyjy/zfcgCjgs/index_1.jhtml', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_liubiao_gg" , 'http://www.bjhd.gov.cn/ggzyjy/zfcgFbgs/index_1.jhtml', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###全国公共资源交易平台(北京.海淀)
def work(conp, **args):
    est_meta(conp, data=data, diqu="北京市海淀区", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=True,
        num=1,
        )
    pass