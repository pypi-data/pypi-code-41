import json
import math

import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zlsrc.util.etl import est_meta, est_html, add_info, est_gg


def f1(driver, num):

    locator = (By.XPATH, '//pre[string-length()>100][contains(string(),"success")]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall('skipCount=(\d+)', url)[0])
    cnum=(cnum//10)+1

    if int(cnum) != num:
        url = re.sub('(?<=skipCount=)\d+', str((num-1)*10), url)
        page_count = len(driver.page_source)
        driver.get(url)

        WebDriverWait(driver, 10).until(lambda driver:len(driver.page_source) != page_count)
        locator = (By.XPATH, '//pre[string-length()>100][contains(string(),"success")]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("pre").get_text()
    contents=json.loads(div)['result']['items']

    data = []
    for c in contents:
        href = c.get('id')
        name = c.get('title')
        diqu = c.get('areas')
        ggstart_time = c.get('creationTime')
        proType = c.get('projectType')
        proNo = c.get('projectNo')
        info=json.dumps({"proType":proType,"proNo":proNo,"diqu":diqu},ensure_ascii=False)

        href = 'http://www.chinapsp.cn/notice_content.html?itemid=' + href
        tmp = [name, ggstart_time, href,info]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    # df['info'] = None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '//pre[string-length()>100][contains(string(),"success")]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page_total=re.findall('"totalCount":(\d+),',driver.page_source)[0]
    page_total=math.ceil(int(page_total)/10)

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="article-con"][string-length()>100]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.5)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.5)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_="article")
    if div == None:
        raise ValueError('div is None')

    return div


data = [

    ["jqita_zhaobiao_gg", 'https://wx.chinapsp.cn/qy/api/services/app/AbpArticles/GetPaged?filter=a.ext2+%3D%3D+%2274166%22+and+a.isDispaly+%3D%3D+%22true%22&sorting=a.creationTime+desc&maxResultCount=10&skipCount=0',
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["jqita_gqita_zhong_liu_gg", 'https://wx.chinapsp.cn/qy/api/services/app/AbpArticles/GetPaged?filter=a.ext2+%3D%3D+%2274167%22+and+a.isDispaly+%3D%3D+%22true%22&sorting=a.creationTime+desc&maxResultCount=10&skipCount=0',
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["jqita_zhongbiao_gg", 'https://wx.chinapsp.cn/qy/api/services/app/AbpArticles/GetPaged?filter=a.ext2+%3D%3D+%2274168%22+and+a.isDispaly+%3D%3D+%22true%22&sorting=a.creationTime+desc&maxResultCount=10&skipCount=0',
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["jqita_biangeng_gg", 'https://wx.chinapsp.cn/qy/api/services/app/AbpArticles/GetPaged?filter=a.ext2+%3D%3D+%2274169%22+and+a.isDispaly+%3D%3D+%22true%22&sorting=a.creationTime+desc&maxResultCount=10&skipCount=0',
     ["name", "ggstart_time", "href", 'info'], f1, f2],

]


###采联采购
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