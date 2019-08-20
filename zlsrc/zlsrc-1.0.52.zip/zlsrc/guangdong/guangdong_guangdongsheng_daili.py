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
    locator = (By.XPATH, '//table[@id="zb_notice_tab"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('page=(\d+)',url)[0]

    if int(cnum) != num:
        url=re.sub('(?<=page=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//table[@id="zb_notice_tab"]/tbody/tr[1]//a').get_attribute('href')[-30:]

        driver.get(url)

        locator = (
            By.XPATH, '//table[@id="zb_notice_tab"]/tbody/tr[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", id="zb_notice_tab").find('tbody')

    dls = div.find_all("tr",recursive=False)
    data = []
    for dl in dls:
        # print(dl)
        href=dl.find('a')['href']
        name=dl.find('a').get_text(strip=True)
        biaohao= dl.find_all('td')[-2].get_text()
        ggstart_time = dl.find_all('td')[-1].get_text().strip('[').strip(']')
        info=json.dumps({"biaohao":biaohao},ensure_ascii=False)
        href='http://gzqunsheng.com'+href
        tmp = [name, ggstart_time, href,info]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    # df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//table[@id="zb_notice_tab"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=driver.find_element_by_xpath('//a[@class="last_page"]').get_attribute('href')

    page_total=re.findall('page=(\d+)',page_total)[0]

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="zb_price_cont"][string-length()>100]')
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
    div = soup.find('div', class_='zb_detail')

    return div



data=[

    ["jqita_zhongbiaohx_gg" , 'http://gzqunsheng.com/info2.php?CateId=2&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhaobiao_gg" , 'http://gzqunsheng.com/info2.php?CateId=1&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://gzqunsheng.com/info2.php?CateId=3&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_gqita_da_bian_gg" , 'http://gzqunsheng.com/info2.php?CateId=4&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###广州群生招标代理有限公司
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