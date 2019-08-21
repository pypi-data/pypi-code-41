import json

import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_tbs, est_meta, est_html


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='gvXmList']/tbody/tr[@class='gridtd'][last()]/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//span[@id='gvXmList_ctl23_lblPage']")
    total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'第(\d+)页', total)[0]

    if int(cnum) != int(num):
        val = driver.find_element_by_xpath("//table[@id='gvXmList']/tbody/tr[@class='gridtd'][last()]/td[2]/a").get_attribute('onclick')
        val = re.findall(r"\('(.*)'\)", val)[0]
        driver.find_element_by_xpath("//input[contains(@id, 'inPageNum')]").clear()
        driver.find_element_by_xpath("//input[contains(@id, 'inPageNum')]").send_keys(num)
        driver.find_element_by_xpath("//input[contains(@id, 'Button1')]").click()

        locator = (By.XPATH, "//table[@id='gvXmList']/tbody/tr[@class='gridtd'][last()]/td[2]/a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='gvXmList').tbody
    lis = div.find_all('tr', class_='gridtd')

    for tr in lis:
        a = tr.find_all('td')[1].a
        try:
            name=a['title']
        except:
            name = a.text.strip()

        ggstart_time=tr.find_all('td')[2].text.strip()
        href=a['onclick']
        if 'http' in href:
            href = href
        else:
            href = re.findall(r"\('(.*)'\)", href)[0]
            href = 'http://www.ciac.sh.cn/xmbjwsbsweb/xmquery/XmDetail.aspx?bjbh=' + href
        info = {}

        bj_num = tr.find_all('td')[0].text.strip()
        if bj_num:info['bj_num']=bj_num

        lx = tr.find_all('td')[3].text.strip()
        if lx:info['lx']=lx
        if info:info=json.dumps(info, ensure_ascii=False)
        else:info= None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@id='gvXmList']/tbody/tr[@class='gridtd'][last()]/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//span[@id='gvXmList_ctl23_lblPage']")
    total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'共(\d+)页', total)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='panel' and contains(@style, 'block')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//iframe[@height="98%"]')
    driver.switch_to_frame(val)
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
    page1 = driver.page_source
    soup1 = BeautifulSoup(page1, 'html.parser')
    div = soup1.find('body')
    if div == None:
        raise ValueError('div is None')
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.ciac.sh.cn/xmbjwsbsweb/xmquery/XmList.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="上海市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_shanghai_shanghai"], total=2, num=1, headless=False)


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = d[-1](driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=d[-2](driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)

