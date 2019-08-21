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
    locator = (By.XPATH, '//ul[@id="divnews"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//span[@class="laypage_total"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=driver.find_element_by_xpath('//span[@class="laypage_curr"]').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//ul[@id="divnews"]/li[1]/a').get_attribute('href')[-20:]
        # print(val)

        search_button = driver.find_element_by_xpath('//input[@class="laypage_skip"]')
        driver.execute_script("arguments[0].value='%s';" % num, search_button)
        ele = driver.find_element_by_xpath('//button[@class="laypage_btn"]')
        driver.execute_script("arguments[0].click()", ele)

        locator = (
            By.XPATH, '//ul[@id="divnews"]/li[1]/a[not(contains(@href,"{val}"))]'.format(val=val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", id='divnews')
    dls = div.find_all("li")
    data = []
    for dl in dls:

        href=dl.find('a')['href']
        name=dl.find('a')['title']

        ggstart_time = dl.find('span',class_='time').get_text()

        href='http://60.6.253.156:8888/sszt-zyjyPortal/'+href

        tmp = [name, ggstart_time, href]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@id="divnews"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//span[@class="laypage_total"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//a[@class="laypage_last"]').get_attribute('data-page')
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="show_nav"][string-length()>100]')
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
    div = soup.find('div', class_='show_containt')

    return div



data=[

["zfcg_zhaobiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_biangeng_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&type=%E5%8F%98%E6%9B%B4%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhongbiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&type=%E4%B8%AD%E6%A0%87%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_liubiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&type=%E5%BA%9F%E6%A0%87%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_dyly_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&type=%E5%85%AC%E7%A4%BA%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],

["gcjs_zhaobiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_biangeng_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&type=%E5%8F%98%E6%9B%B4%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiaohx_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&type=%E4%B8%AD%E6%A0%87%E5%85%AC%E7%A4%BA', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&type=%E4%B8%AD%E6%A0%87%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_liubiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal//zyjyPortal/portal/tradeNotice?regionCode=130500&category=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&type=%E5%BA%9F%E6%A0%87%E5%85%AC%E5%91%8A', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###邢台市公共资源交易网
def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省邢台市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=False,
        num=1,
        )
    pass