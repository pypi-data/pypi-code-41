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
    locator = (By.XPATH, '//section[@id="articles"]/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('p(\d+).html',url)[0]

    if int(cnum) != num:
        url=re.sub('(?<=p)\d+(?=.html)',str(num),url)
        val = driver.find_element_by_xpath(
            '//section[@id="articles"]/div[1]//a').get_attribute('href')[-15:]

        driver.get(url)

        locator = (
            By.XPATH, '//section[@id="articles"]/div[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("section", id="articles")
    dls = div.find_all("div",recursive=False)

    data = []
    for dl in dls:
        href=dl.find('a')['href']
        name=dl.find('a').get_text()
        ggstart_time = dl.find('span',attrs={"title":'发布时间'}).get_text().strip()
        href='http://www.ynzzhw.cn'+href
        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//section[@id="articles"]/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//div[@class="pager"]').text

    page_total=re.findall('1/(\d+)',page_total)[0]

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//section[@class="article-content"][string-length()>100]')
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
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', id='article')



    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.ynzzhw.cn/article/c15/p1.html', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://www.ynzzhw.cn/article/c16/p1.html', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###云南中咨海外咨询有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="云南省", **args)
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