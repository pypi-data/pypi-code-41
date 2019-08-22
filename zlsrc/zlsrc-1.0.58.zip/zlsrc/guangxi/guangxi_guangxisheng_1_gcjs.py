import json

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_meta, est_html, add_info,est_meta_large



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='mian_list'][string-length()>50]")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', class_='mian_list')
    return div


def f1(driver, num):

    locator = (By.XPATH, '//table[@class="table_text"]/tbody/tr[child::td][1]/td/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-35:]

    locator = (By.XPATH, '//div[@class="pagination"]/label[2]')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    cnum = re.findall('(\d+)',txt)[0]

    if int(cnum) != int(num):
        driver.execute_script("turnPage(%s);"%num)

        locator = (By.XPATH, '//table[@class="table_text"]/tbody/tr[child::td][1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="table_text"]/tbody/tr[child::td]')
    for content in content_list:
        name = content.xpath("./td[1]/a/@title")[0].strip()

        if "categoryId=90" in driver.current_url:
            ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        else:
            ggstart_time = content.xpath("./td[last()-1]/text()")[0].strip()
        url = re.findall("\'([^\']+)\'",content.xpath("./td[1]/a/@href")[0].strip())[0]

        if "categoryId=89" not in driver.current_url:
            hangye = content.xpath("./td[2]/span/@title")[0].strip()
            area = content.xpath("./td[3]/span/@title")[0].strip()
            info_tmp = {'area': area, 'hangye': hangye}
        else:
            area = content.xpath("./td[2]/span/@title")[0].strip()
            info_tmp = {'area':area,}
        info = json.dumps(info_tmp,ensure_ascii=False)
        temp = [name, ggstart_time, url,info]
        print(temp)

        data.append(temp)

    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="pagination"]/label[1]')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    total_page = re.findall('(\d+)',txt)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["gcjs_zgysjg_gg",
     "http://zbtb.gxi.gov.cn:9000/xxfbcms/category/qualifyBulletinList.html?searchDate=1994-07-03&dates=300&categoryId=92&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhaobiao_gg",
     "http://zbtb.gxi.gov.cn:9000/xxfbcms/category/bulletinList.html?searchDate=1994-07-03&dates=300&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiaohx_gg",
     "http://zbtb.gxi.gov.cn:9000/xxfbcms/category/candidateBulletinList.html?searchDate=1994-07-03&dates=300&categoryId=91&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiao_gg",
     "http://zbtb.gxi.gov.cn:9000/xxfbcms/category/resultBulletinList.html?searchDate=1994-07-03&dates=300&categoryId=90&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_biangeng_gg",
     "http://zbtb.gxi.gov.cn:9000/xxfbcms/category/changeBulletinList.html?searchDate=1994-07-03&dates=300&categoryId=89&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

###广西壮族自治区招标投标公共服务平台
def work(conp, **arg):
    est_meta_large(conp, data=data, diqu="广西省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    # # url = "http://zbtb.gxi.gov.cn:9000/xxfbcms/category/qualifyBulletinList.html?searchDate=1994-07-03&dates=300&categoryId=92&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word="
    # for d in data:
    #
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver, 2)
    #     for ur in df.values.tolist()[:4]:
    #         try:
    #             print(f3(driver, ur[2])[:10])
    #         except:print(1111111,ur[2])
    #     driver.get(d[1])
    #     print(f2(driver))

    #
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "guangxisheng"],num=1,ipNum=0,headless=False)
