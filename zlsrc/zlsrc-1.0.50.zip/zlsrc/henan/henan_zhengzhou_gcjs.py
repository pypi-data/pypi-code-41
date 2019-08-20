import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zlsrc.util.etl import est_tbs, est_meta, est_html, add_info



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="list-div"]/ul/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()-1]').text
    cnum = re.findall('第(.+?)页', cnum)[0].strip()

    if cnum != str(num):

        val = driver.find_element_by_xpath('//div[@class="list-div"]/ul/li[1]//a').get_attribute('href')[-30:-5]
        driver.execute_script('PageJump(%s);' % num)
        locator = (By.XPATH, '//div[@class="list-div"]/ul/li[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('div', class_="list-div").find('ul').find_all('li',recursive=False)

    for tr in trs:

        href = tr.find('div',class_='col-10').find('a')['href']
        name = tr.find('div',class_='col-10').find('a').get_text().strip()
        ggstart_time = tr.find('div',class_='col-2').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.zzjs.com.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="list-div"]/ul/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()-1]').text

    total = re.findall('共(.+?)页', total)[0].strip()

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="news-info"][string-length()>50]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
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

    div = soup.find('div', class_="news-info")


    return div


data = [


    ["gcjs_zhaobiao_gg", "http://www.zzjs.com.cn/TenderAnnouncement/Index",[ "name", "ggstart_time", "href", "info"],f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.zzjs.com.cn/BidPublicity/Index",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgys_gg", "http://www.zzjs.com.cn/Qualification/Index",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河南省郑州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "henan_zhengzhou"],num=1)