import random
import pandas as pd
import re
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, est_meta
from zlsrc.util.fake_useragent import UserAgent


tt_url = None

def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    # tt_url = driver.current_url
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        "k": "getnewsList",
        "pageIndex": num-1,
        "pageCount": 10,
        "KW":"",
    }
    # 下载超时
    timeOut = 60
    if proxies:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    else:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        html_data = json.loads(html)
        lis = html_data["newslist"]
        data = []
        for tr in lis:
            name = tr['title']
            ggstart_time = tr['pubdate']
            url = tr['url']
            # print(url)
            if 'indexmc_two.htm' in url:
                href = 'http://www.ggzymc.cn/ceinwz/hgmc/' + url
            else:
                href = 'http://www.ggzymc.cn/ceinwz/' + url.split('/', maxsplit=1)[1]
            tmp = [name, ggstart_time, href]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        df['info'] = None
        return df



def f2(driver):
    global tt_url
    tt_url = None
    tt_url = driver.current_url
    page_num = get_pageall(tt_url)
    driver.quit()
    return int(page_num)


def get_pageall(tt_url):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        "k": "getnewsList",
        "pageIndex": 1,
        "pageCount": 10,
        "KW":"",
    }
    # 下载超时
    timeOut = 60
    if proxies:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    else:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        html_data = json.loads(html)
        total = html_data['total']
        num = int(total)
        return num


def f3(driver, url):
    driver.get(url)
    if 'indexmc_two.htm' in url:
        locator = (By.XPATH, "//div[contains(@id, 'vsb_content')][string-length()>100]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        before = len(driver.page_source)
        time.sleep(1)
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
        div = soup.find('div', id='divNewsList')
        return div


    locator = (By.XPATH, "//table[@width='100%'][string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    page1 = driver.page_source
    soup1 = BeautifulSoup(page1, 'html.parser')
    div1 = soup1.find_all('table')[0]
    if 'id="frmBestwordHtml' in str(driver.page_source):
        driver.switch_to_frame('frmBestwordHtml')
        if '找不到文件或目录' in str(driver.page_source):
            return '找不到文件或目录'
        locator = (By.XPATH, "//div[contains(@class, 'Section')][string-length()>3] | //embed[@id='plugin']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 1
    else:
        locator = (By.XPATH, "//table[@width='75%'] | //div[@class='wrap'] | //div[@class='page']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 2

    before = len(driver.page_source)
    time.sleep(1)
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
        div = soup.find('body')
        if div == None:
            div = soup.find('embed', id='plugin')
        divs1 = str(div1) + str(div)
        div = BeautifulSoup(divs1, 'html.parser')
    elif flag == 2:
        div = soup.find_all('table')[0]
    else:
        raise ValueError

    if '有效期失效不能访问' in div:
        raise ValueError
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.ggzymc.cn/ceinwz/wxfirst.ashx?&newsid=1000&jsgc=0100000&FromUrl=jsgc_gg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_gqita_bian_bu_gg",
     "http://www.ggzymc.cn/ceinwz/wxfirst.ashx?&jsgc=00110000&FromUrl=jsgc_by",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.ggzymc.cn/ceinwz/wxfirst.ashx?&newsid=1002&jsgc=00000100&FromUrl=jsgc_jg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.ggzymc.cn/ceinwz/wxfirst.ashx?&newsid=1002&jsgc=00000010&FromUrl=jsgc_jg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhaobiao_gg",
     "http://www.ggzymc.cn/ceinwz/wxfirst.ashx?&newsid=1004&zfcg=0100000&FromUrl=zfcg_gg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_bian_bu_gg",
     "http://www.ggzymc.cn/ceinwz/wxfirst.ashx?&zfcg=00110000&FromUrl=zfcg_by",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhongbiao_gg",
     "http://www.ggzymc.cn/ceinwz/wxfirst.ashx?&newsid=1006&zfcg=00000100&FromUrl=zfcg_jg",
     ["name", "ggstart_time", "href", "info"], f1,  f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省麻城市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_hubei_macheng"])


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
    #     df=f1(driver, 10)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # d = f3(driver, 'http://www.ggzymc.cn/ceinwz/hgmc/indexmc_two.htm?id=4173&FromUrl=nourl')
    # print(d)
