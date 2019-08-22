import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json

import time

from zlsrc.util.etl import est_html, est_meta, add_info



def f1(driver, num):
    locator = (By.XPATH, "//table[@id='NewList']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        cnum = soup.find('span', id='Pager1_CurPage').text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='NewList']/tbody/tr[1]/td/a").get_attribute('href')[-30:]
        if num > int(cnum):
            t = num - int(cnum)
            for i in range(t):
                locator = (By.XPATH, "//table[@id='NewList']/tbody/tr[1]/td/a")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                driver.execute_script("javascript:__doPostBack('Pager1$lb_Next','')")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            cnum_1 = soup.find('span', id='Pager1_CurPage').text.strip()
            if num != int(cnum_1):
                raise TimeoutError
        if num < int(cnum):
            t = int(cnum) - num
            for i in range(t):
                locator = (By.XPATH, "//table[@id='NewList']/tbody/tr[1]/td/a")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                driver.execute_script("javascript:__doPostBack('Pager1$lb_Prev','')")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            cnum_1 = soup.find('span', id='Pager1_CurPage').text.strip()
            if num != int(cnum_1):
                raise TimeoutError

        locator = (By.XPATH, "//table[@id='NewList']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", id='NewList').tbody
    lis = div.find_all("tr", class_='nslist')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find("td", align="right").text.strip()
        span = re.findall(r'\[(.*)\]', span)[0]
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.yajsgh.gov.cn/website/' + link.split('/',maxsplit=1)[1]
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@id='NewList']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@id='Pager1_Pages']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        num = soup.find('span', id='Pager1_Pages').text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='smt'][string-length()>10] | //iframe[@id='wl'][string-length()>10]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('div', id='smt')
    if div == None:
        div = soup.find('iframe', id='wl')
        if div:
            driver.switch_to.frame('wl')
            locator = (By.XPATH, "//div[@class='content']//table//tr[string-length()>10] | //div[@class='openwin-accordion-content'][string-length()>10]")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
            div=soup.find('body', class_='PageBgNoScroll')
        else:
            raise ValueError
    if div == None:raise ValueError

    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=211011001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_shuili_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=211011002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'水利'}), f2],

    ["gcjs_zhaobiao_jiaotong_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=211011003",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'交通'}), f2],

    ["gcjs_zhaobiao_gongxinwei_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=21101104",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'工信委'}), f2],

    ["gcjs_zhaobiao_zhengfu_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=211011007",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'政府采购'}), f2],

    ["gcjs_zhaobiao_qita_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=211011005",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'其他项目'}), f2],

    ["gcjs_zhaobiao_guotuziyuan_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=211011006",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'国土资源'}), f2],

    ["gcjs_zhongbiao_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=21100401",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_shuili_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=21100402",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'水利'}), f2],

    ["gcjs_zhongbiao_jiaotong_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=21100403",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'交通'}), f2],

    ["gcjs_zhongbiao_zhengfu_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=21100407",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'政府采购'}), f2],

    ["gcjs_zhongbiao_guotuziyuan_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=21100406",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'国土资源'}), f2],

    ["gcjs_zhongbiao_qita_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=21100405",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'其他项目'}), f2],

    ["gcjs_zhongbiao_gongxinwei_gg",
     "http://www.yajsgh.gov.cn/webSite/main/yanewslist7.aspx?fcol=21100404",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'lx':'工信委'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省延安市", **args)
    est_html(conp, f=f3, **args)

# 修改时间：2019/8/15
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "shanxi_yanan"])
    #
    # for d in data[3:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     # print(url)
    #     # driver.get(url)
    #     # df = f2(driver)
    #     # print(df)
    #     # driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 2)
    #     # print(df.values)
    #     for f in df[2].values:
    #         print(f)
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://www.yajsgh.gov.cn/website/main/yadetailpage1.aspx?fid=3c12a8c4-5a99-405a-a413-9901f15aa646&fcol=21100403')
    # print(df)

