import json
import random
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//div[@class='item-list']/table/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//a[@class='cur-ye']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='item-list']/table/tbody/tr[last()]/td/a").get_attribute('href')[-30:]
        driver.execute_script("pagination({});".format(num))

        locator = (By.XPATH, "//div[@class='item-list']/table/tbody/tr[last()]/td/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='item-list').table.tbody
    lis = table.find_all('tr')
    url = driver.current_url
    for tr in lis[1:]:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('td')[-1].text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'https://www.dongfengtc.com' + link
        info = {}
        if 'gongGaoType' in url:
            xm_num = tr.find_all('td')[1].text.strip()
            if xm_num:info['xm_num']=xm_num
        else:
            biaoduan_num = tr.find_all('td')[1].text.strip()
            if biaoduan_num:info['biaoduan_num']=biaoduan_num
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='item-list']/table/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    num = driver.find_element_by_xpath("//div[@class='page-container']/a[last()-1]").text.strip()
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if 'id="iframepage"' in str(driver.page_source):
        driver.switch_to_frame('iframepage')
        locator = (By.XPATH, "//div[contains(@class, 'maign_top')][string-length()>100]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        flag = 1
    else:
        locator = (By.XPATH, "//div[contains(@class, 'text')][string-length()>100]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        flag = 2
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
    if flag == 1:
        div = soup.find('div', class_=re.compile(r'maign_top'))
    elif flag == 2:
        div = soup.find('div', class_='container1').find('div', class_=re.compile(r'^text$'))
    else:raise ValueError
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "https://www.dongfengtc.com/gg/ggList",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zgys_gg",
     "https://www.dongfengtc.com/gg/zgysList",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_biangeng_gg",
     "https://www.dongfengtc.com/gg/bgggList",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_kongzhijia_gg",
     "https://www.dongfengtc.com/gg/zbkzjList",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zgysjg_gg",
     "https://www.dongfengtc.com/gg/zgscList",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "https://www.dongfengtc.com/gg/zbhxrList",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "https://www.dongfengtc.com/gg/zbjgList",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_wsxj_gg",
     "https://www.dongfengtc.com/gg/toXinXiList?gongGaoType=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'询价'}), f2],

    ["jqita_gqita_bian_bu_wsxj_gg",
     "https://www.dongfengtc.com/gg/toXinXiList?gongGaoType=6",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'询价'}), f2],

    ["jqita_zhongbiao_wsxj_gg",
     "https://www.dongfengtc.com/gg/toXinXiList?gongGaoType=7",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'询价'}), f2],
    ####
    ["jqita_zhaobiao_wsjj_gg",
     "https://www.dongfengtc.com/gg/pmjmList?gongGaoType=8",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'竞价'}), f2],

    ["jqita_gqita_bian_bu_wsjj_gg",
     "https://www.dongfengtc.com/gg/pmjmList?gongGaoType=9",
     ["name", "ggstart_time", "href", "info"],  add_info(f1, {'zblx':'竞价'}), f2],

    ["jqita_zhongbiao_wsjj_gg",
     "https://www.dongfengtc.com/gg/pmjmList?gongGaoType=10",
     ["name", "ggstart_time", "href", "info"],  add_info(f1, {'zblx':'竞价'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="东风交易中心", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_dongfengtc_com"], )


    # for d in data[-6:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


