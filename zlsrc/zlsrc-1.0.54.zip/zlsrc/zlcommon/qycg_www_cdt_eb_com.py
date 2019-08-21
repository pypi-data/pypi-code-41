import math
import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json



from zlsrc.util.etl import est_tbs, est_meta, est_html, add_info, est_meta_large



def f1(driver, num):
    locator = (By.XPATH, "//div[@style='display: block;']//tbody[contains(@id,'tbody')]/tr[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = driver.find_element_by_xpath('//div[@style="display: block;"]//span[@class="current"]').text


    if int(cnum) != num:
        val = driver.find_element_by_xpath("//div[@style='display: block;']//tbody[contains(@id,'tbody')]/tr[1]").get_attribute('onclick')[-30:-2]

        input_ = driver.find_element_by_xpath('//div[@style="display: block;"]//input[@class="jump-index"]')
        input_.click()
        input_.clear()
        input_.send_keys(str(num))
        driver.find_element_by_xpath('//div[@style="display: block;"]//a[last()]').click()


        locator = (By.XPATH, '//div[@style="display: block;"]//tbody[contains(@id,"tbody")]/tr[1][not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('tbody', id='tbody1')
    trs = div.find_all('tr', recursive=False)
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[0].get_text()
        href = tr['onclick']
        ggstart_time = tds[2].get_text()
        cgdw = tds[1].get_text()

        str_mark = re.findall('get.+?tail', href)[0]
        id_mark = re.findall("\('(.+?)'\)", href)[0]


        if 'fzbcg' in url:
            str2_dict = {'getPricedetail': 1, 'getOnlydetail': 2, 'getCompeteTalkdetail': 3,
                         'getBiddingProjectdetail': 4, 'getChangedetail': 0, 'getResultdetail': 6}
            if str2_dict[str_mark] == 0:
                href = "http://www.cdt-eb.com/web/DetailsNotice.html?param={id_mark}". \
                    format(id_mark=id_mark)
            else:
                href = "http://www.cdt-eb.com/web/DetailsNotice.html?param={id_mark}&str={str_mar}". \
                    format(id_mark=id_mark, str_mar=str2_dict[str_mark])

        else:
            str1_dict = {'getPredetail': 1, 'getChgdetail': 3, 'getNoticedetail': 2, 'getResultdetail': 4}
            href = "http://www.cdt-eb.com/web/zbcg_detail.html?param={id_mark}&str={str_mar}". \
                format(id_mark=id_mark, str_mar=str1_dict[str_mark])
        info={'cgdw':cgdw}
        info=json.dumps(info,ensure_ascii=False)

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, "//div[@style='display: block;']//tbody[contains(@id,'tbody')]/tr[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@style="display: block;"]//div[@class="pagination"]/a[1]').text
    total = re.findall('共(.+?)条记录', total)[0].strip()
    total = math.ceil(int(total) / 30)

    driver.quit()

    return total





def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, '//div[@class="sup_part2"][string-length()>10] | //div[@id="pricedetails"][string-length()>10]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_="sup_part2")
    if div == None:
        div=soup.find('div',id='pricedetails')

    return div


data = [
    ["qycg_zhaobiao_xunjia_gg", "http://www.cdt-eb.com/web/fzbcg_2.html#menu=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'询价'}), f2],
    ["qycg_dyly_gg", "http://www.cdt-eb.com/web/fzbcg_2.html#menu=2",["name", "ggstart_time", "href", "info"],f1, f2],
    ["qycg_zhaobiao_tanpan_gg", "http://www.cdt-eb.com/web/fzbcg_2.html#menu=3",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'竞争性谈判'}), f2],
    ["qycg_zhaobiao_jingpai_gg", "http://www.cdt-eb.com/web/fzbcg_2.html#menu=4",["name", "ggstart_time", "href", "info"],add_info(f1,{'zbfs':'竞拍'}), f2],
    ["qycg_zhongbiao_gg", "http://www.cdt-eb.com/web/fzbcg_2.html#menu=5",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'非公开'}), f2],


    ["qycg_zgys_gg", "http://www.cdt-eb.com/web/zbcg_bggg.html#menu=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhaobiao_gg", "http://www.cdt-eb.com/web/zbcg_bggg.html#menu=2",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_biangeng_gg", "http://www.cdt-eb.com/web/zbcg_bggg.html#menu=3",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiaohx_gg", "http://www.cdt-eb.com/web/zbcg_bggg.html#menu=4",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="大唐集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_cdt_ed_com"],headless=False,num=1)
    pass