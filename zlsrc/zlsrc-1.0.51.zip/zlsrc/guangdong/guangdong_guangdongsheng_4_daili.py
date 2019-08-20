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
    locator = (By.XPATH, '//table[@class="mainTable"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('pageIndex=(\d+)',url)[0]

    if int(cnum) != num:
        url=re.sub('(?<=pageIndex=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//table[@class="mainTable"]//tr[2]//a').get_attribute('href')[-30:]
        driver.get(url)
        locator = (
            By.XPATH, '//table[@class="mainTable"]//tr[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", class_="mainTable")
    dls = div.find_all("tr")[1:]

    data = []
    for dl in dls:
        tds=dl.find_all('td')
        href=dl.find('a')['href']
        name=dl.find('a').get_text(strip=True)

        ggstart_time=tds[3].get_text()
        bianhao=tds[0].get_text()
        diqu=tds[2].get_text()
        info=json.dumps({"bianhao":bianhao,"diqu":diqu},ensure_ascii=False)

        href='http://www.gdydzb.com'+href
        tmp = [name, ggstart_time, href,info]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    # df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//table[@class="mainTable"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//a[@class="aborder2"][2]').get_attribute('href')

    page_total=re.findall('pageIndex=(\d+)',page_total)[0]

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="nyMain-cont"][string-length()>100]')
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
    div = soup.find('div',class_="nySider-news")
    if div == None:
        raise ValueError('div is None')

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.gdydzb.com/front/channel.action?pageSize=12&code=root_xxgg_zbgg&pageIndex=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiaohx_gg" , 'http://www.gdydzb.com/front/channel.action?pageSize=12&code=root_xxgg_zbjg&pageIndex=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_gqita_da_bian_gg" , 'http://www.gdydzb.com/front/channel.action?pageSize=12&code=root_xxgg_cqtz&pageIndex=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###广东远东招标代理有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
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