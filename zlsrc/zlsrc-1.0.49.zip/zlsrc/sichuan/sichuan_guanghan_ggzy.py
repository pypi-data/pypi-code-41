import random
import pandas as pd
import re
import requests
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
from zlsrc.util.fake_useragent import UserAgent



endTime = time.strftime('%Y-%m-%d',time.localtime(time.time()))


def f1(driver, num):
    url = driver.current_url
    menuCode = re.findall(r'menuCode=(.*)', url)[0]
    stsrt_url = url.rsplit('/', maxsplit=1)[0]
    Data = {
        'page': (num - 1),
        'time': 'customize',
        'areaCode': '510681',
        'menuCode': menuCode,
        'menuTypeCode': '',
        'contentTypeCode': '',
        'keyname': '',
        'startTime': '2016-11-28',
        'endTime': endTime,
        'areaCodeFlag': '',
        # '_csrf': 'e84db454-ee48-42f5-b33a-7c61fd718952',
    }
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    sesion = requests.session()
    res = sesion.post(url=stsrt_url, headers=headers, data=Data)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        page = res.text
        if page:
            soup = BeautifulSoup(page, 'html.parser')
            div = soup.find('div', class_="search-result")
            lis = div.find_all('li')
            data_list = []
            for li in lis:
                a = li.find('a')
                title = a.text.strip()
                link = 'http://www.dyggzy.com' + a['href'].strip()
                span = li.find('span', class_="time").text.strip()
                try:
                    td = re.findall(r'\[(.*?)\]', title)[0]
                except:
                    td = ''
                p = li.find('p')
                try:
                    yw_type = p.find_all('span')[0].text.strip()
                except:
                    yw_type = ''
                try:
                    xx_type = p.find_all('span')[1].text.strip()
                except:
                    xx_type = ''
                a = {"diqu": td, 'yw_type':yw_type, 'xx_type':xx_type}
                info = json.dumps(a, ensure_ascii=False)
                tmp = [title, span, link, info]
                data_list.append(tmp)
            df = pd.DataFrame(data_list)
            return df



def f2(driver):
    WebDriverWait(driver, 10).until(lambda driver: len(driver.current_url) > 10)
    url = driver.current_url
    menuCode = re.findall(r'menuCode=(.*)', url)[0]
    stsrt_url = url.rsplit('/', maxsplit=1)[0]
    Data = {
        'page': 0,
        'time': 'customize',
        'areaCode': '510681',
        'menuCode': menuCode,
        'menuTypeCode': '',
        'contentTypeCode': '',
        'keyname': '',
        'startTime': '2016-11-28',
        'endTime': endTime,
        'areaCodeFlag': '',
        # '_csrf': 'e84db454-ee48-42f5-b33a-7c61fd718952',
    }
    num = get_pagenum(stsrt_url, Data)
    driver.quit()
    return num


def get_pagenum(stsrt_url, Data):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
        }

    sesion = requests.session()
    res = sesion.post(url=stsrt_url, headers=headers, data=Data)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        page = res.text
        # print(page)
        if page:
            soup = BeautifulSoup(page, 'html.parser')
            div = soup.find('div', class_="pagenations")
            atrs = div.find_all('span')[0].text.strip()
            num = re.findall(r'共(\d+)页', atrs)[0]
            if int(num) == 0: raise ValueError
            return int(num)




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='detail-box'][string-length()>140]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='content'][string-length()>40] | //div[@id='content']//img")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 1
    except:
        if 'id="pdf_iframe"' in str(driver.page_source):
            flag = 2
        else:raise ValueError

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
        div = soup.find('div', id="oneDetail")
        if div == None:
            div = soup.find('div', class_="detail-box")
    elif flag == 2:
        div = soup.find('div', class_="detail-box")
    else:raise ValueError
    return div


data = [
    ["gcjs_gqita_gg",
     "http://ggzyxx.deyang.gov.cn/pub/showJyxxContent/menuCode=JYGCJS",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_gg",
     "http://ggzyxx.deyang.gov.cn/pub/showJyxxContent/menuCode=JYCG",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_gg",
     "http://ggzyxx.deyang.gov.cn/pub/showJyxxContent/menuCode=JYQT",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'其他交易'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省广汉市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","guanghan"])

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
    #     df=f1(driver, 3)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
