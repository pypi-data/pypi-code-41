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
    locator = (By.XPATH, '//tr[@height="26"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('nowPage=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=nowPage=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//tr[@height="26"][1]//a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//tr[@height="26"][1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find_all('tr',height="26")

    for tr in div:
        href=tr.find('a')['href'].strip()
        name=tr.find('a').get_text(strip=True)
        ggstart_time=tr.find_all('td',class_='th_4')[1].get_text(strip=True)
        pro_index=tr.find_all('td',class_='th_4')[0].get_text(strip=True)
        if 'http' in href:
            href = href
        else:
            href = 'http://gk.wh.cn/xxgkweb/blue/' + href

        info=json.dumps({'pro_index':pro_index},ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@height="26"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//select[@name="nowPage"]/option[last()]').text
        total=re.findall('第(\d+)页',page)[0]
    except:
        total=1

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@class="bw"][string-length()>50]')
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

    div = soup.find('table',class_="bw")


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["zfcg_zhaobiao_1_gg", "http://gk.wh.cn/xxgkweb/blue/unit.jsp?name=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&unit=758540107&xxfl_id=860102&sort=2&nowPage=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiaohx_1_gg", "http://gk.wh.cn/xxgkweb/blue/unit.jsp?name=%E4%B8%AD%E6%A0%87%E5%80%99%E9%80%89%E4%BA%BA%E5%85%AC%E7%A4%BA&unit=758540107&xxfl_id=860103&sort=2&nowPage=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_1_gg", "http://gk.wh.cn/xxgkweb/blue/unit.jsp?name=%E4%B8%AD%E6%A0%87%E7%BB%93%E6%9E%9C%E5%85%AC%E7%A4%BA&xxfl_id=860104&unit=758540107&sort=2&nowPage=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg", "http://gk.wh.cn/xxgkweb/blue/unit.jsp?name=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&unit=758540107&xxfl_id=830100&sort=1&nowPage=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://gk.wh.cn/xxgkweb/blue/unit.jsp?name=%E4%B8%AD%E6%A0%87%E5%85%AC%E7%A4%BA&unit=758540107&xxfl_id=830200&sort=1&nowPage=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://gk.wh.cn/xxgkweb/blue/unit.jsp?name=%E9%87%87%E8%B4%AD%E5%85%AC%E5%91%8A&unit=758540107&xxfl_id=820100&sort=1&nowPage=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://gk.wh.cn/xxgkweb/blue/unit.jsp?name=%E4%B8%AD%E6%A0%87%E3%80%81%E6%88%90%E4%BA%A4%E5%85%AC%E5%91%8A&unit=758540107&xxfl_id=820200&sort=1&nowPage=1",["name", "ggstart_time", "href", "info"], f1, f2],

]




##芜湖市人民政府(办公室)
def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省芜湖市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "wuhu"], total=2, headless=True, num=1)



