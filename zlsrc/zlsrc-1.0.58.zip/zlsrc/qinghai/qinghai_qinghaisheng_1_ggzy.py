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
    locator = (By.XPATH, '//table[@id="tblInfo"]')
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
    div = soup.find('table', id="tblInfo")

    return div


def f1(driver, num):


    locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-60:]
    locator = (By.XPATH, "//font[@color='red']")
    cnum = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%num)
        locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="MoreInfoList1_DataGrid1"]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td[2]/a/@title")[0].strip()
        ggstart_time = content.xpath("./td[3]/text()")[0].strip()
        url = 'http://qhzbtb.qhwszwdt.gov.cn' + content.xpath("./td[2]/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] =None
    return df


def f2(driver):

    locator = (By.XPATH, '//font[@color="blue"][2]')
    total_page = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
    driver.quit()
    return int(total_page)




data = [
    #
    ["gcjs_zhaobiao_gg",
     "http://qhzbtb.qhwszwdt.gov.cn/qhweb/jyxx/005001/005001001/MoreInfo.aspx?CategoryNum=005001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zgys_gg",
     "http://qhzbtb.qhwszwdt.gov.cn/qhweb/jyxx/005001/005001005/MoreInfo.aspx?CategoryNum=005001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_biangeng_gg",
     "http://qhzbtb.qhwszwdt.gov.cn/qhweb/jyxx/005001/005001002/MoreInfo.aspx?CategoryNum=005001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_kongzhijia_gg",
     "http://qhzbtb.qhwszwdt.gov.cn/qhweb/jyxx/005001/005001003/MoreInfo.aspx?CategoryNum=005001003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiao_gg",
     "http://qhzbtb.qhwszwdt.gov.cn/qhweb/jyxx/005001/005001004/MoreInfo.aspx?CategoryNum=005001004",
     ["name", "ggstart_time", "href", "info"], f1, f2],





    #
    ["zfcg_zhaobiao_gg",
     "http://qhzbtb.qhwszwdt.gov.cn/qhweb/jyxx/005002/005002001/MoreInfo.aspx?CategoryNum=005002001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["zfcg_biangeng_gg",
     "http://qhzbtb.qhwszwdt.gov.cn/qhweb/jyxx/005002/005002002/MoreInfo.aspx?CategoryNum=005002002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["zfcg_zhongbiao_gg",
     "http://qhzbtb.qhwszwdt.gov.cn/qhweb/jyxx/005002/005002004/MoreInfo.aspx?CategoryNum=005002004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **arg):
    est_meta_large(conp, data=data, diqu="青海省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':

    for d in data:

        driver = webdriver.Chrome()
        url = d[1]
        driver.get(url)
        df = f1(driver, 2)
        #
        for u in df.values.tolist()[:4]:
            f3(driver, u[2])
        driver.get(url)

        print(f2(driver))
    # work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "qinghaisheng1"])
    # driver = webdriver.Chrome()
    # driver.get("http://ggzy.ah.gov.cn/login.do?method=beginlogin")
    # print(f2(driver))