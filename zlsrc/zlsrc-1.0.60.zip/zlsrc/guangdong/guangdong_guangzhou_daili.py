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
    locator = (By.XPATH, '(//table[@id="tablist"]/tbody/tr[2]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//a[@class="cur"]').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '(//table[@id="tablist"]/tbody/tr[2]//a)[1]').get_attribute('href')[-30:]

        driver.execute_script("PageContext.PageNav.go(%s,%s);" %(num,page_total))

        locator = (
            By.XPATH, '(//table[@id="tablist"]/tbody/tr[2]//a)[1][not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", id="tablist").find('tbody')

    dls = div.find_all("tr",recursive=False)[1:-1]
    data = []
    for dl in dls:
        # print(dl)
        href=dl.find('a')['href']
        name=dl.find('a').get_text(strip=True)
        ggstart_time = dl.find_all('td')[-1].get_text()

        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    global page_total
    locator = (By.XPATH, '(//table[@id="tablist"]/tbody/tr[2]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//span[@class="nav_pagenum"]').text

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="xly"][string-length()>500]')
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
    div = soup.find('div', class_='xly')

    return div



data=[

["zfcg_gqita_zhao_zhong_gg" , 'http://lingshui.hainan.gov.cn/xxgkall.html?ClassInfoId=2456', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###陵水黎族自治县人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="海南省陵水黎族自治县", **args)
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