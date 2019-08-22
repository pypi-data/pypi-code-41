from math import ceil
import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, est_meta, add_info


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='tLayer-1']/table/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//li[@class='on']/span")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='tLayer-1']/table/tbody/tr[last()]//a").get_attribute('href')[-30:]
        url = re.sub('page=[0-9]+','page=%d'%num, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='tLayer-1']/table/tbody/tr[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='tLayer-1').table.tbody
    trs = table.find_all('tr', recursive=False)
    for tr in trs:
        a = tr.find('a')
        name = a.text.strip()
        ggstart_time = tr.find_all('td')[-1].text.strip()
        href = 'http://220.163.15.148'+a['href']
        info = {}
        zbr = tr.find_all('td')[-3].text.strip()
        if 'WinningList' in url:
            if zbr:info['jsdw']=zbr
        elif 'WinningResultNoticeList' in url:
            if zbr:info['zhongbr']=zbr
        elif 'InBuildingList' in url:
            if zbr: info['sgxkz_num'] = zbr
        else:
            if zbr:info['zbr']=zbr

        zblx = tr.find_all('td')[-2].text.strip()
        if 'InBuildingList' in url:
            if zblx: info['sgdw'] = zblx
        else:
            if zblx: info['zblx'] = zblx

        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='tLayer-1']/table/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='jump fl']/span[1]")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    total = re.findall(r'\d+', txt)[0]
    num = ceil(int(total)/15)
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@class, 'tLayer')]//table[string-length()>100]")
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
    div = soup.find('div', class_=re.compile('tLayer'))
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://220.163.15.148/Announcement/BiddingAnnouncementList?page=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://220.163.15.148/Announcement/WinningList?page=1",
     ["name", "ggstart_time", "href", "info"], f1,  f2],

    ["gcjs_zhongbiao_gg",
     "http://220.163.15.148/Announcement/WinningResultNoticeList?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zjgc_gg",
     "http://220.163.15.148/Announcement/InBuildingList?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'在建工程'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="云南省", **args)
    est_html(conp, f=f3, **args)

# 网站加载慢
# 修改日期：2019/8/15
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_yunnan_yunnan"])


    # for d in data:
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
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://220.163.15.148/Announcement/InBuildingDetial?pwID=c1ca1888-e2ea-4957-aaa5-73f5c1b37bbd ')
    # print(df)


