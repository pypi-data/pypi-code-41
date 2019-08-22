import json

import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_tbs, est_meta, est_html, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//table[@id='MoreInfoListGG_DataGrid1']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath("//div[@id='MoreInfoListGG_Pager']/table/tbody/tr/td/font[3]").text

    if int(cnum) != int(num):
        val = driver.find_element_by_xpath("//table[@id='MoreInfoListGG_DataGrid1']/tbody/tr[last()]//a").get_attribute('href')[-30:]
        driver.execute_script("javascript:__doPostBack('MoreInfoListGG$Pager','{}')".format(num))

        locator = (By.XPATH, "//table[@id='MoreInfoListGG_DataGrid1']/tbody/tr[last()]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='MoreInfoListGG_DataGrid1').tbody
    lis = div.find_all('tr')

    for tr in lis:
        a = tr.find('a')
        try:
            name=a['title']
        except:
            name = a.text.strip()

        ggstart_time=tr.find_all('td')[-1].text.strip()
        href=a['href']
        if 'http' in href:
            href = href
        else:
            href = 'http://www.zjbid.cn' + href
        info = {}
        ln = len(a.find_all('font'))
        for i in range(int(ln)):
            if i == 0:
                diqu = a.find_all('font')[0].text.strip()
                info['diqu']=diqu
            elif i == 1:
                lx = a.find_all('font')[1].text.strip()
                info['lx']=lx
        if info:info=json.dumps(info, ensure_ascii=False)
        else:info= None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@id='MoreInfoListGG_DataGrid1']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@id='MoreInfoListGG_Pager']/table/tbody/tr/td/font[2]")
    total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    try:
        locator = (By.XPATH, "//td[@id='TDContent'][string-length()>100]")
        WebDriverWait(driver, 2).until(EC.presence_of_element_located(locator))
    except:
        locator = (By.XPATH, "//body[string-length()=0]")
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))
        locator = (By.XPATH, "//head[string-length()=0]")
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))
        return '网页不可爬取'
    locator = (By.XPATH, "//td[@id='TDContent'][string-length()>100]")
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
    div = soup.find('table', id='tblInfo')
    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.zjbid.cn/zjwz/template/default/GGInfo.aspx?CategoryNum=001001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_zhongbiaohx_gg", "http://www.zjbid.cn/zjwz/template/default/GGInfo.aspx?CategoryNum=001001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.zjbid.cn/zjwz/template/default/GGInfo.aspx?CategoryNum=001001009",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="浙江省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_zhejiang_zhejiang"], total=2, headless=True, num=1)

    #
    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     # driver.get(url)
    #     # df = d[-1](driver)
    #     # print(df)
    #     # driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=d[-2](driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://www.zjbid.cn/zjwz/InfoDetail/Default.aspx?InfoID=715db684-067d-4fcc-af51-478781666ca1&CategoryNum=001001005')
    # print(df)

