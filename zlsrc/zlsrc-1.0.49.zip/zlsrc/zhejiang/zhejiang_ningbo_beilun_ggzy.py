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
    locator = (By.XPATH, '//div[@class="default_pgContainer"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = re.findall('pageNum=(\d+)',url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//div[@class="default_pgContainer"]/li[1]/a').get_attribute('href')[-20:]

        url=re.sub('(?<=pageNum=)\d+',str(num),url)
        driver.get(url)

        locator = (
            By.XPATH, '//div[@class="default_pgContainer"]/li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", class_="default_pgContainer")
    dls = div.find_all("li")
    data = []
    for dl in dls:

        href=dl.find('a')['href']
        name=dl.find('a').get_text(strip=True)

        ggstart_time = dl.span.get_text().strip('[').strip(']')


        if 'http' in href:
            href = href
        else:
            href = 'http://www.bl.gov.cn' + href

        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="default_pgContainer"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//span[@class="default_pgTotalPage"]').text

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="zoom"][string-length()>50]')
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
    div = soup.find('div', class_='bt-mian')

    return div



data=[

["gcjs_zhaobiao_gg" , 'http://www.bl.gov.cn/col/col114306/index.html?uid=323236&pageNum=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiaohx_gg" , 'http://www.bl.gov.cn/col/col114307/index.html?uid=323236&pageNum=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhaobiao_gg" , 'http://www.bl.gov.cn/col/col114311/index.html?uid=323236&pageNum=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhongbiao_gg" , 'http://www.bl.gov.cn/col/col114322/index.html?uid=323236&pageNum=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

["jqita_gqita_zhao_zhong_gg" , 'http://www.bl.gov.cn/col/col127922/index.html?uid=323236&pageNum=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["jqita_zhaobiao_gg" , 'http://www.bl.gov.cn/col/col114349/index.html?uid=323236&pageNum=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["jqita_zhongbiao_gg" , 'http://www.bl.gov.cn/col/col133076/index.html?uid=323236&pageNum=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###宁波市北仑区人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省宁波市北仑区", **args)
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