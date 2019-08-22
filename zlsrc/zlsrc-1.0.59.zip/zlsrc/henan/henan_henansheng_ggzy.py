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
from zlsrc.util.etl import est_tbs, est_meta, est_html



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="bd-content1"]/div/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('Paging=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=Paging=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//div[@class="bd-content1"]/div/table//tr[1]//a').get_attribute('href')[-40:-20]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="bd-content1"]/div/table//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='bd-content1').find('div')
    lis = div.find('table').find_all('tr')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('td',align='right').get_text().strip(']').strip('[')
        if 'http' in href:
            href = href
        else:
            href = 'http://www.hnggzy.com' + href

        tmp = [name, ggstart_time, href]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="bd-content1"]/div/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//div[@id="Paging"]//td[@class="pageout"][last()]').get_attribute('onclick')
        total = re.findall('Paging=(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="bottom-bg1"]//div[@class="row"]/div[2][string-length()>100]')
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

    div = soup.find('div', class_='bottom-bg1').find('div',class_='row').find_all('div',recursive=False)[1]

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002001/002001001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002001/002001002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002001/002001003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_yucai_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002001/002001004/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002001/002001005/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002002/002002001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002002/002002002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002002/002002003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002002/002002004/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002005/002005001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_biangeng_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002005/002005002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiaohx_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002005/002005003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg", "http://www.hnggzy.com/hnsggzy/jyxx/002006/002006002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "henan_henan"], total=2, headless=True, num=1)



