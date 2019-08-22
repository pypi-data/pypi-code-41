import json
import random
import re
from datetime import datetime, timedelta
import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time

_name_ = 'www_jczh100_com'


def f1(driver, num):
    driver.get(re.sub('page=\d+', 'page=' + str(num), driver.current_url))
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,"//ul[@class='pinfolist pinfolist01']/li")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='pinfolist pinfolist01']/li")
    data = []
    for content in content_list:
        diqu = content.xpath('./div/div/span[1]/text()')[0].strip()
        name = content.xpath('./div/a/span[2]/text()')[0].strip()
        try:
            trade = content.xpath('./div/div/span[3]/text()')[0].strip()
        except:trade ='None'
        ggtype = content.xpath('./div/div/span[2]/text()')[0].strip()
        ggstart_time = re.findall('发布时间：(.+)', content.xpath('./div[@class="date fl"]/p[2]/text()')[0].strip())[0]

        href = 'http://www.jczh100.com' + content.xpath('./a/@href')[0].strip()
        info_temp = {}
        try:
            left_days = content.xpath('./div[@class="date fl"]/p[1]/span[2]/text()')[0].strip()
            endtime = (datetime.strptime(ggstart_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=int(left_days))).strftime('%Y-%m-%d %H:%M:%S')
            info_temp.update({'endtime':endtime})
        except:
            pass
        info_temp.update({'ggtype': ggtype,'diqu':diqu,"trade":trade})

        info = json.dumps(info_temp, ensure_ascii=False)
        temp = [name, ggstart_time, href,info]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    page_temp = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//div[@class="pinfotit"]/span'))).text
    total_page = math.ceil(int(page_temp)/15)

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="box_l fl"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='box_l fl')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=1&xinxi=1&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=2&xinxi=1&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=3&xinxi=1&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=4&xinxi=1&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhonbiao_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=5&xinxi=1&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],





    ["zfcg_zhaobiao_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=1&xinxi=2&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=2&xinxi=2&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=3&xinxi=2&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=4&xinxi=2&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhonbiao_gg",
     "http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=5&xinxi=2&page=1#somap",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

#江西省精彩纵横采购咨询有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="精彩纵横网", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qycg_www_jczh100_com"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://www.jczh100.com/index/tendering/li.html?zhuanti=&et=&industry=&t=z&hangye=&so=&quyu=&gonggao=1&xinxi=1&page=2#somap')
    # # print(f2(driver))
    #
    # f1(driver, 1)
    # print(f2(driver))
    # f1(driver, 21)
    work(conp)
