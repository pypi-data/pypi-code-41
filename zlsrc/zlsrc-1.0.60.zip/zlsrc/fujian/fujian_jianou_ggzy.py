import random
from math import ceil

import pandas as pd
import re
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import add_info,est_meta,est_html
from zlsrc.util.fake_useragent import UserAgent


def f1_requests(datas, start_url, s=0):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    res = requests.get(url=start_url, headers=headers, data=datas)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            html = json.loads(html)
            datalist = html["data"]
            data_list = []
            for data in datalist:
                if s == 3:
                    title = data['TITLE']
                    td = data['TM']
                    link = "http://www.joztb.com/views/tradeCenter/jianou/trade.html?id="+data['ID']+"&type=articles&ons=%E4%B9%A1%E9%95%87%E6%8B%9B%E6%A0%87"
                    try:
                        yw_type = data['TYPE_NAME']
                    except:
                        yw_type = ''
                    info = json.dumps({'yw_type': yw_type}, ensure_ascii=False)
                    tmp = [title, td, link, info]
                    data_list.append(tmp)
                else:
                    title = data['NAME']
                    td = data['PUBLISHED_TIME']
                    link = data['URL']
                    if s == 2:
                        link = link.strip() + "/zhongbiaogg"
                    try:
                        diqu = data['AREANAME']
                    except:
                        diqu = ''
                    try:
                        yw_type = data['BIG_TYPE_TEXT']
                    except:
                        yw_type = ''
                    try:
                        hy_type = data['TYPE_TEXT']
                    except:
                        hy_type = ''
                    info = json.dumps({'diqu':diqu, 'yw_type':yw_type, 'hy_type':hy_type}, ensure_ascii=False)
                    tmp = [title, td, link, info]
                    data_list.append(tmp)
            df = pd.DataFrame(data_list)
            return df



def f1(driver, num):
    url = driver.current_url
    if "type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A" in url:
        datas = {
            'method': 'Web.GetJiaoYiList',
            'pageindex': '{}'.format(num),
            'pagesize': '15',
            'BIG_TYPE': 'A',
            'NAME': '',
            'TYPE': '',
            'AREA_CODE': '35',
            'PUBLISHED_TIME_START': '2016-11-01',
            'PUBLISHED_TIME_END': '',
            'STATUS': '',
        }
        start_url = "http://www.enjoy5191.com:9001/api/GetDataHandler.ashx?PLATFORM_CODE=E3507837011"
        df = f1_requests(datas, start_url, s=1)
        return df

    elif "type=%E4%B8%AD%E6%A0%87%E5%85%AC%E7%A4%BA" in url:
        datas = {
            'method': 'Web.GetJiaoYiList',
            'pageindex': '{}'.format(num),
            'pagesize': '15',
            'BIG_TYPE': '',
            'NAME': '',
            'TYPE': '',
            'AREA_CODE': '',
            'PUBLISHED_TIME_START': '',
            'PUBLISHED_TIME_END': '',
            'STATUS': '',
            'in_status': '3,4'
        }
        start_url = "http://www.enjoy5191.com:9001/api/GetDataHandler.ashx?PLATFORM_CODE=E3507837011"
        df = f1_requests(datas, start_url, s=2)
        return df

    else:
        datas = {
            'method':'Web.GetNewsList',
            'in_type':'73e4fff0-9a96-42d9-8300-542d29c22b06',
            'pageindex': '{}'.format(num),
            'pagesize':'15',
            'TITLE':'',
            'CREATE_TM_START':'1900-01-01',
            'CREATE_TM_END':'',
        }
        start_url = "http://www.enjoy5191.com:9001/api/GetDataHandler.ashx?PLATFORM_CODE=E3507837011"
        df = f1_requests(datas, start_url, s=3)
        return df


def f2_requests(data, start_url):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    res = requests.get(url=start_url, headers=headers, data=data)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            html = json.loads(html)
            total = html["total"]
            if int(total) == 0:raise ConnectionError
            page_all = ceil(int(total)/15)
            return page_all



def f2(driver):
    url = driver.current_url
    if "type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A" in url:
        data = {
            'method': 'Web.GetJiaoYiList',
            'pageindex': '1',
            'pagesize': '15',
            'BIG_TYPE': 'A',
            'NAME': '',
            'TYPE': '',
            'AREA_CODE': '35',
            'PUBLISHED_TIME_START': '2016-11-01',
            'PUBLISHED_TIME_END': '',
            'STATUS': '',
        }
        start_url = "http://www.enjoy5191.com:9001/api/GetDataHandler.ashx?PLATFORM_CODE=E3507837011"
        num_total = f2_requests(data, start_url)
        driver.quit()
        return int(num_total)

    if "type=%E4%B9%A1%E9%95%87%E6%8B%9B%E6%A0%87" in url:
        locator = (By.XPATH, "//*[contains(text(),'非电子标')]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
    try:
        locator = (By.XPATH, "//span[@class='pageInfo']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num_total = re.findall(r'(\d+)', str)[0]
    except:
        num_total = 1

    driver.quit()
    return int(num_total)



def f3(driver, url):
    if "/zhongbiaogg" in url:
        url = url.rsplit('/', maxsplit=1)[0]
        driver.get(url)
        try:
            locator = (By.XPATH, "(//*[contains(text(),'中标公示')])[1]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        except:
            locator = (By.XPATH, "(//*[contains(text(),'中标公告')])[1]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()

        locator = (By.XPATH, "//iframe[@class='myFrame'] | //iframe[@id='ifrEdit'] | //iframe[@id='myFrame']")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        try:
            dd = driver.find_element_by_xpath("//iframe[@class='myFrame'] | //iframe[@id='myFrame']")
        except:
            dt = driver.find_element_by_xpath("//iframe[@id='ifrEdit']")
            driver.switch_to_frame(dt)
            locator = (By.XPATH, "//iframe[@id='ifrEdit1']")
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
            dd = driver.find_element_by_xpath("//iframe[@id='ifrEdit1']")
        driver.switch_to_frame(dd)
        time.sleep(2)
        try:
            locator = (By.XPATH, "//div[@id='templateContent'][string-length()>400] | //div[@class='app'][string-length()>400]")
            WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(locator))
            flag = 1
        except:
            try:
                locator = (By.XPATH, "//div[@class='bidderPublic'][string-length()>400]")
                WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located(locator))
                flag = 2
            except:
                locator = (By.XPATH, "//embed[@id='plugin']")
                WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located(locator))
                flag = 3
        before = len(driver.page_source)
        time.sleep(1)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(1)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        if flag == 1:
            div = soup.find('div', class_='wrap')
            if div == None:
                div = soup.find('div', class_='app')
        elif flag == 2:
            div = soup.find('div', class_='bidderPublic')
        elif flag == 3:
            div = soup.find('embed', id='plugin')['src']
        else:
            raise ValueError
        return div

    elif 'http://www.joztb.com/views/tradeCenter/jianou/trade.html' in url:
        driver.get(url)
        locator = (By.XPATH, "//div[@class='md-content'][string-length()>100]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        before = len(driver.page_source)
        time.sleep(1)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(1)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find('div', class_='md-content')
        return div

    else:
        driver.get(url)
        locator = (By.XPATH, "//iframe[@class='myFrame'] | //iframe[@id='ifrEdit'] | //iframe[@id='myFrame']")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        try:
            dd = driver.find_element_by_xpath("//iframe[@class='myFrame'] | //iframe[@id='myFrame']")
        except:
            dt = driver.find_element_by_xpath("//iframe[@id='ifrEdit']")
            driver.switch_to_frame(dt)
            locator = (By.XPATH, "//iframe[@id='ifrEdit1']")
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
            dd = driver.find_element_by_xpath("//iframe[@id='ifrEdit1']")
        driver.switch_to_frame(dd)
        time.sleep(2)
        try:
            locator = (By.XPATH, "//div[@id='main'][string-length()>400]")
            WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(locator))
            flag = 1
        except:
            try:
                locator = (By.XPATH, "//div[@class='view'][string-length()>400]")
                WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located(locator))
                flag = 2
            except:
                locator = (By.XPATH, "//embed[@id='plugin']")
                WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located(locator))
                flag = 3

        before = len(driver.page_source)
        time.sleep(1)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(1)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        if flag == 1:
            div = soup.find('div', class_='wrap')
        elif flag == 2:
            div = soup.find('div', class_='view')
        elif flag == 3:
            div = soup.find('embed', id='plugin')
        else:raise ValueError
        return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://www.joztb.com/views/tradeCenter/jianou/trade.html?type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.joztb.com/views/tradeCenter/jianou/trade.html?type=%E4%B8%AD%E6%A0%87%E5%85%AC%E7%A4%BA",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhao_zhong_xiangzhen_gg",
     "http://www.joztb.com/views/tradeCenter/jianou/trade.html?type=%E4%B9%A1%E9%95%87%E6%8B%9B%E6%A0%87",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省建瓯市",**args)
    est_html(conp,f=f3,**args)


# 修改日期：2019/7/9
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","fujian","jianou"])


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
    #     df=f1(driver, 23)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://106.75.116.110:8210/fjebid/jypt.html?type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&tpid=59786337a6e3252290f36390&tpTitle=%E5%BB%BA%E7%93%AF%E5%B8%82%E4%B8%9C%E5%B3%B0%E9%95%87%E5%9D%A4%E5%8F%A3%E3%80%81%E4%BA%95%E6%AD%A7%E5%B0%8F%E5%AD%A6%E8%BF%90%E5%8A%A8%E5%9C%BA%E5%8F%8A%E9%99%84%E5%B1%9E%E6%94%B9%E9%80%A0%E5%B7%A5%E7%A8%8B/zhongbiaogg')
    # print(df)

