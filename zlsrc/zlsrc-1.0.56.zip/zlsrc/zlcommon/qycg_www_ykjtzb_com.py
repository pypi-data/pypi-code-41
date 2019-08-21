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
    locator = (By.XPATH, "//ul[@id='list1']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//a[@class='pag-cur']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@id='list1']/li[1]/a").get_attribute('href')[-20:]
        driver.execute_script('page({})'.format(num))

        locator = (By.XPATH, "//ul[@id='list1']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("ul", id='list1')
    data = []
    lis = ul.find_all('li')
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = li.find('span', class_='bidLink').text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.ykjtzb.com' + link
        span = a.find_all("em")[-1].text.strip()
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@id='list1']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='pag-txt']/em[last()]")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='article-content'][string-length()>50]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('div', class_='article-content')
    return div


data = [
    ["qycg_zhaobiao_huowu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg1hw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'货物'}), f2],

    ["qycg_zhaobiao_gongcheng_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg1gc/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'工程'}), f2],

    ["qycg_zhaobiao_fuwu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg1fw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'服务'}), f2],
    # ####
    ["qycg_biangeng_huowu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg6hw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'货物'}), f2],

    ["qycg_biangeng_gongcheng_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg6gc/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'工程'}), f2],

    ["qycg_biangeng_fuwu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg6fw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'服务'}), f2],
    # ####
    ["qycg_zhongbiaohx_huowu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg2hw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'货物'}), f2],

    ["qycg_zhongbiaohx_gongcheng_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg2gc/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'工程'}), f2],

    ["qycg_zhongbiaohx_fuwu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg2fw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'服务'}), f2],

    ###
    ["qycg_zhongbiao_huowu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg3hw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '货物'}), f2],

    ["qycg_zhongbiao_gongcheng_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg3gc/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '工程'}), f2],

    ["qycg_zhongbiao_fuwu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg3fw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '服务'}), f2],

    ###
    ["qycg_gqita_huowu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg4hw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '货物'}), f2],

    ["qycg_gqita_gongcheng_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg4gc/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '工程'}), f2],

    ["qycg_gqita_fuwu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg4fw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '服务'}), f2],

    ###
    ["qycg_zhaobiao_erci_huowu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg5hw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '货物', 'gglx':'二次公告'}), f2],

    ["qycg_zhaobiao_erci_gongcheng_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg5gc/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '工程',  'gglx':'二次公告'}), f2],

    ["qycg_zhaobiao_erci_fuwu_gg",
     "http://www.ykjtzb.com/cms/channel/zbywgg5fw/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'lx': '服务', 'gglx':'二次公告'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="兖矿集团", **args)
    est_html(conp, f=f3, **args)


# 网址变更
# 更改日期：2019/7/6
# 网址：http://www.ykjtzb.com/cms/index.htm
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_ykjtzb_com"])

    # for d in data[4:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 1)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)