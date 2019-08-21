
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



from zlsrc.util.etl import add_info,est_meta,est_html,est_tbs





def f1(driver, num):
    # locator = (By.XPATH, "(//font[@class='currentpostionfont'])[last()]")
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    locator = (By.XPATH, "//tr[@height='25'][1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@class='huifont']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = re.findall(r'(\d+)/', st)[0]
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//tr[@height='25'][1]/td/a").get_attribute('href')[-50:]
        if "Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//tr[@height='25'][1]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//tr[@height='25'][1]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", cellspacing='3')
    trs = table.find_all("tr", height="25")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        try:
            link = a["href"]
        except:
            continue
        td = tr.find("font", color="#000000").text.strip()
        link = "http://www.lssggzy.com" + link.strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    # html_data = str(driver.page_source)
    if ("本栏目暂时没有内容" in str(driver.page_source)) or ('404' in driver.title):
        return 0
    locator = (By.XPATH, "//tr[@height='25'][1]/td/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    s = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = int(re.findall(r'/(\d+)', s)[0])
    driver.quit()
    return num



def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//table[@style='overflow:hidden' and @width='100%'][string-length()>300]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('table', attrs={"style":"overflow:hidden", 'width':'100%'})
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001001/071001001003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["gcjs_biangeng_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001002/071001002003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zsjg_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001003/071001003003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001004/071001004003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001005/071001005003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["gcjs_xiaoer_zhaobiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001006/071001006001/071001006001003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_xiaoer_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001006/071001006002/071001006002003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_xiaoer_zhongbiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001006/071001006003/071001006003003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["zfcg_zhaobiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002002/071002002003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002003/071002003003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],



    ["zfcg_zhongbiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002005/071002005003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["qsy_zhaobiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071005/071005001/071005001003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["qsy_gqita_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071005/071005002/071005002003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省龙泉市",**args)
    est_html(conp,f=f3,**args)

# 最新修改日期：2019/7/10
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","zhejiang","longquan"])


    # for d in data:
    #     url = d[1]
    #     print(url)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     f = f2(driver)
    #     print(f)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     df = f1(driver, 1)
    #     print(df.values)
    #     for i in df[2].values:
    #         dd = f3(driver, i)
    #         print(dd)
