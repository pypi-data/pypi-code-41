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

from zlsrc.util.etl import est_meta_large
from zlsrc.util.etl import est_meta, est_html, add_info


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='zbd_left fl'] | //iframe[@id='ifDetail'] | //div[@class='mian_list'][string-length()>100]")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    try:
        driver.switch_to.frame("ifDetail")
        mark=1
    except:
        mark=0

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

    if mark==1:
        div=soup.find('div', class_='mian_list')
        return div

    div = soup.find('div', class_='zbd_left fl')
    if div == None:
        div = soup.find('div', class_='mian_list')

    driver.switch_to.parent_frame()

    return div





def f1(driver, num):
    locator = (By.XPATH, '//div[@class="iweifa_right_nr"]/p[1]/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
    locator = (By.XPATH, '//span[@class="page-cur"]')
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    if int(cnum) != int(num):
        url = re.sub('pageNum=\d+','pageNum='+str(num),driver.current_url)
        driver.get(url)

        locator = (By.XPATH, '//div[@class="iweifa_right_nr"]/p[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="iweifa_right_nr"]/p')
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = 'http://www.ahtba.org.cn' + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f11(driver, num):
    locator = (By.XPATH, "//table[@class='table_text']/tbody/tr[last()]/td[1]/a")
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')
    val = re.findall(r"javascript:urlOpen\('(.*)'\)", val)[0]

    locator = (By.XPATH, "//div[@class='pagination']/label[2]")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    if int(cnum) != int(num):
        url = re.sub('page=\d+','page=%d' % num,driver.current_url)
        driver.get(url)

        locator = (By.XPATH, '//table[@class="table_text"]/tbody/tr[last()]/td[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', class_='table_text').tbody
    trs = table.find_all('tr')
    for tr in trs[1:]:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('td')[3].text.strip()
        href = a['href']
        href = re.findall(r"javascript:urlOpen\('(.*)'\)", href)[0]
        info = {}
        diqu = tr.find_all('td')[1].text.strip()
        diqu = re.findall(r'(\w+)', diqu)[0]
        if diqu:info['diqu']=diqu
        if 'http://220.178.99.166:9000/xxfbcms/search/change.html' in driver.current_url:
            yuangg_name= tr.find_all('td')[-1].text.strip()
            if yuangg_name:info['yuangg_name']=yuangg_name
            yuangg_href= tr.find_all('a')[-1]['href']
            yuangg_href = re.findall(r"javascript:urlOpen\('(.*)'\)", yuangg_href)[0]
            if yuangg_href:info['yuangg_href']=yuangg_href
        else:
            ggend_time = tr.find_all('td')[-1].text.strip()
            if ggend_time:info['ggend_time']=ggend_time

        if info:info = json.dumps(info,  ensure_ascii=False)
        else:info = None

        temp = [name, ggstart_time, href, info]
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//a[@class="page_show"]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text

    total_page = re.findall('\/ (\d+)', txt)[0]
    driver.quit()
    return int(total_page)


def f21(driver):
    locator = (By.XPATH, "//div[@class='pagination']/label[1]")
    num = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(num)



data = [
    #
    ["gcjs_zhaobiao_1_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=714&scid=713&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zgysjg_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=714&scid=596&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_zhaobiao_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=714&scid=597&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_zhongbiao_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=569&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=739&scid=740&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=739&scid=741&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=569&scid=604&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_biangeng_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=569&scid=605&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=569&scid=606&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["jqita_zgys_gj_gg",
     "http://220.178.99.166:9000/xxfbcms/search/qualify.html?searchDate=1994-07-29&dates=300&categoryId=92&startcheckDate=2000-07-29&endcheckDate=2019-07-29&page=1",
     ["name", "ggstart_time", "href", "info"], f11, f21],

    ["jqita_zhaobiao_gj_gg",
     "http://220.178.99.166:9000/xxfbcms/search/bulletin.html?searchDate=1994-07-29&dates=300&categoryId=88&startcheckDate=2000-07-29&endcheckDate=2019-07-29&page=1",
     ["name", "ggstart_time", "href", "info"], f11, f21],

    ["jqita_zhongbiaohx_gj_gg",
     "http://220.178.99.166:9000/xxfbcms/search/candidate.html?searchDate=1994-07-29&dates=300&categoryId=91&startcheckDate=2000-07-29&endcheckDate=2019-07-29&page=1",
     ["name", "ggstart_time", "href", "info"], f11, f21],

    ["jqita_zhongbiao_gj_gg",
     "http://220.178.99.166:9000/xxfbcms/search/result.html?searchDate=1994-07-29&dates=300&categoryId=90&startcheckDate=2000-07-29&endcheckDate=2019-07-29&page=1",
     ["name", "ggstart_time", "href", "info"], f11, f21],

    ["jqita_biangeng_gj_gg",
     "http://220.178.99.166:9000/xxfbcms/search/change.html?searchDate=1994-07-29&dates=300&categoryId=89&startcheckDate=2000-07-29&endcheckDate=2019-07-29&page=1",
     ["name", "ggstart_time", "href", "info"], f11, f21],
]


##f3 为swf

###安徽省招投标信息网
def work(conp, **arg):
    est_meta_large(conp, data=data, diqu="安徽省", **arg)
    est_html(conp, f=f3, **arg)

# 修改日期：2019/7/29

if __name__ == '__main__':
    # url = "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=714&scid=597&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15"
    # for d in data:
    #
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver, 2)
    #     for ur in df.values.tolist():
    #         print(f3(driver, ur[2]))
    #     driver.get(d[1])
    #     print(f2(driver))

    #
    # work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "anhuisheng"])

    # for d in data[-1:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f21(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f11(driver, 3)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    driver=webdriver.Chrome()
    f=f3(driver,'http://220.178.99.166:9000/biddingBulletin/2019-01-25/32.html')
    print(f)