import json
import time

import pandas as pd
import re
import math
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zlsrc.util.etl import est_meta, est_html, est_gg, add_info,gg_existed




def f1(driver, num):

    locator = (By.XPATH, '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath(
        '//div[@class="bidMessage"]//ul[@class="on"]//a[@class="current"] | //div[@class="bidMessage"]//ul[not(@style)]//a[@class="current"]').text.strip()

    if (int(cnum) != num) or num == 1:
        if num == 1:
            val = '第一页'
        else:
            val = driver.find_element_by_xpath(
                '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]//a').get_attribute(
                "href").rsplit('/',maxsplit=1)[1]

        driver.execute_script("page_1({},1500,'');".format(num))

        locator = (By.XPATH,
                   '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        if num == page_total:
            ctext = driver.find_element_by_xpath(
                '//div[@class="bidMessage"]//ul[@class="on"]//div[@class="list_pages"]//span | //div[@class="bidMessage"]//ul[not(@style)]//div[@class="list_pages"]//span').text
            ctext = int(re.findall('(\d+)条记录', ctext)[0])

            ccount = ctext % 1500
        else:
            ccount = 1500
        locator = (By.XPATH,
                   '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody[count(tr)=%s]' % ccount)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='download_table').find('tbody')
    trs = div.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[1]['title']
        href = tds[1].a['href']
        jy_type = tds[2].get_text()
        ggstart_time = tds[3].get_text()
        diqu = tds[1].span.get_text().strip(']').strip('[') if tds[1].span else None
        if diqu:
            info = {"diqu": diqu, 'jy_type': jy_type}
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = {'jy_type': jy_type}
            info = json.dumps(info, ensure_ascii=False)

        if 'http' in href:
            href = href
        else:
            href = 'http://www.sxbid.com.cn' + href

        tmp = [name, href, ggstart_time, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f4(driver, num):
    locator = (
    By.XPATH, '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath(
        '//div[@class="bidMessage"]//ul[@class="on"]//a[@class="current"] | '
        '//div[@class="bidMessage"]//ul[not(@style)]//a[@class="current"]').text.strip()

    if (int(cnum) != num) or (num == 1):
        if num == 1:
            val = '第一页'
        else:
            val = driver.find_element_by_xpath(
                '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2]').get_attribute(
                "onclick").rsplit('/',maxsplit=1)[1]
        driver.execute_script("page_1({},1500,'');".format(num))

        locator = (By.XPATH,
        '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2][not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        if num == page_total:
            ctext = driver.find_element_by_xpath(
                '//div[@class="bidMessage"]//ul[@class="on"]//div[@class="list_pages"]//span | '
                '//div[@class="bidMessage"]//ul[not(@style)]//div[@class="list_pages"]//span').text
            ctext = int(re.findall('(\d+)条记录', ctext)[0])

            ccount = ctext % 1500
        else:
            ccount = 1500

        locator = (By.XPATH,
                   '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody[count(tr)=%s]' % ccount)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='download_table').find('tbody')
    trs = div.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[1]['title']
        href = tds[1]['onclick']
        href = re.findall('goURL\((.+\.html)', href)[0].strip("'")
        jy_type = tds[2].get_text()
        ggstart_time = tds[3].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.sxbid.com.cn' + href

        info = {'jy_type': jy_type}
        info = json.dumps(info, ensure_ascii=False)

        tmp = [name, href, ggstart_time, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df




def f1_cdc(driver, num):

    locator = (By.XPATH, '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath(
        '//div[@class="bidMessage"]//ul[@class="on"]//a[@class="current"] | //div[@class="bidMessage"]//ul[not(@style)]//a[@class="current"]').text.strip()


    if int(cnum) != num:

        val = driver.find_element_by_xpath(
            '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]//a').get_attribute(
            "href").rsplit('/',maxsplit=1)[1]

        driver.execute_script("page_1({},15,'');".format(num))

        locator = (By.XPATH,
                   '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='download_table').find('tbody')
    trs = div.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[1]['title']
        href = tds[1].a['href']
        jy_type = tds[2].get_text()
        ggstart_time = tds[3].get_text()
        diqu = tds[1].span.get_text().strip(']').strip('[') if tds[1].span else None
        if diqu:
            info = {"diqu": diqu, 'jy_type': jy_type}
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = {'jy_type': jy_type}
            info = json.dumps(info, ensure_ascii=False)

        if 'http' in href:
            href = href
        else:
            href = 'http://www.sxbid.com.cn' + href

        tmp = [name, href, ggstart_time, info]
        # print(tmp)
        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f4_cdc(driver, num):
    locator = (
    By.XPATH, '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath(
        '//div[@class="bidMessage"]//ul[@class="on"]//a[@class="current"] | '
        '//div[@class="bidMessage"]//ul[not(@style)]//a[@class="current"]').text.strip()

    if int(cnum) != num:

        val = driver.find_element_by_xpath(
            '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2]').get_attribute(
            "onclick").rsplit('/',maxsplit=1)[1]
        driver.execute_script("page_1({},15,'');".format(num))

        locator = (By.XPATH,
        '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2][not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))



    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='download_table').find('tbody')
    trs = div.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[1]['title']
        href = tds[1]['onclick']
        href = re.findall('goURL\((.+\.html)', href)[0].strip("'")
        jy_type = tds[2].get_text()
        ggstart_time = tds[3].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.sxbid.com.cn' + href

        info = {'jy_type': jy_type}
        info = json.dumps(info, ensure_ascii=False)

        tmp = [name, href, ggstart_time, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df




def f2(driver):
    global page_total
    locator = (
    By.XPATH, '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath(
        '//div[@class="bidMessage"]//ul[not(@style)]/div[@class="pagination"]//span').text
    total = re.findall('共(\d+?)页', page)[0]

    total = math.ceil(int(total) / 100)
    page_total = total
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//form[@id="loginForm"] | //div[@class="page_main"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))

    try:
        driver.find_element_by_xpath('//div[@class="page_main"]')
    except:
        driver.find_element_by_xpath('//form[@id="loginForm"]')
        return '登录'

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
    div = soup.find('div', class_="page_main")


    return div


data = [

    ###包含:变更,招标,控制价
    ["dianzi_zhaobiao_gg","http://www.sxbid.com.cn/f/list-3d6e34806adf48d5a59ad94f6f31deb5.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],
    ["dianzi_zhongbiaohx_gg","http://www.sxbid.com.cn/f/list-0aba50622c38448a87f83c3104f04b53.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],
    ["dianzi_zhongbiao_gg","http://www.sxbid.com.cn/f/list-5579131cdc344620ae11555919316acf.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],

    ["dianzi_gqita_biangengzbfs_gg","http://www.sxbid.com.cn/f/list-64a95c1eb7b9448393d668838a6923ee.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],add_info(f4,{"gclx":"变更招标方式"}),f2],

    # ###要登录
    ["jqita_zhaobiao_gg","http://www.sxbid.com.cn/f/list-3d6e34806adf48d5a59ad94f6f31deb5.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_zhongbiaohx_gg","http://www.sxbid.com.cn/f/list-0aba50622c38448a87f83c3104f04b53.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_zhongbiao_gg","http://www.sxbid.com.cn/f/list-5579131cdc344620ae11555919316acf.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_gqita_biangengzbfs_gg","http://www.sxbid.com.cn/f/list-64a95c1eb7b9448393d668838a6923ee.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f4,{"gclx":"变更招标方式",'hreftype':'不可抓网页'}),f2],

    ["feigong_zhaobiao_gg", "http://www.sxbid.com.cn/f/list-f368055b9dd748089851eba6519b205f.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],
    ["feigong_zhongbiaohx_gg", "http://www.sxbid.com.cn/f/list-44ec6e4a351946b7bf347c057cfde33e.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],
    ["feigong_zhongbiao_gg", "http://www.sxbid.com.cn/f/list-b18c9f09c5b2476cb08db02884511b9b.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],

]

data_cdc = [

    ###包含:变更,招标,控制价
    ["dianzi_zhaobiao_gg","http://www.sxbid.com.cn/f/list-3d6e34806adf48d5a59ad94f6f31deb5.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],
    ["dianzi_zhongbiaohx_gg","http://www.sxbid.com.cn/f/list-0aba50622c38448a87f83c3104f04b53.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],
    ["dianzi_zhongbiao_gg","http://www.sxbid.com.cn/f/list-5579131cdc344620ae11555919316acf.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],

    ["dianzi_gqita_biangengzbfs_gg","http://www.sxbid.com.cn/f/list-64a95c1eb7b9448393d668838a6923ee.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],add_info(f4,{"gclx":"变更招标方式"}),f2],

    # ###要登录
    ["jqita_zhaobiao_gg","http://www.sxbid.com.cn/f/list-3d6e34806adf48d5a59ad94f6f31deb5.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_zhongbiaohx_gg","http://www.sxbid.com.cn/f/list-0aba50622c38448a87f83c3104f04b53.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_zhongbiao_gg","http://www.sxbid.com.cn/f/list-5579131cdc344620ae11555919316acf.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_gqita_biangengzbfs_gg","http://www.sxbid.com.cn/f/list-64a95c1eb7b9448393d668838a6923ee.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f4,{"gclx":"变更招标方式",'hreftype':'不可抓网页'}),f2],

    ["feigong_zhaobiao_gg", "http://www.sxbid.com.cn/f/list-f368055b9dd748089851eba6519b205f.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],
    ["feigong_zhongbiaohx_gg", "http://www.sxbid.com.cn/f/list-44ec6e4a351946b7bf347c057cfde33e.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],
    ["feigong_zhongbiao_gg", "http://www.sxbid.com.cn/f/list-b18c9f09c5b2476cb08db02884511b9b.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],

]


##### 注意
##### 部分网页在特定时间段内需要登录,过了此时间就不用登录
##### 需定时将gg_html表中page='登录'的对象删除重新爬取

def work(conp, **args):
    if gg_existed(conp):
        est_meta(conp, data=data_cdc, diqu="山西省", **args)
    else:
        est_meta(conp, data=data, diqu="山西省", **args)

    est_html(conp, f=f3, **args)

# 详情页需要设置headless=False爬取
# 山西省招标投标公共服务平台
if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "shanxi1", "shanxi"]
    #
    work(conp=conp, num=1, cdc_total=None, headless=False, ipNum=0)


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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://www.sxbid.com.cn/f/view-6796f0c147374f85a50199b38ecb0af6-107732.html?loginFlag=loginAndPayAndTime')
    # print(df)
