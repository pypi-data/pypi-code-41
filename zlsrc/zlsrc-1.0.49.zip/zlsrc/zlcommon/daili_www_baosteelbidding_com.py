import random
from math import ceil

import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//tr[@bgcolor='#E6E6E6'][last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//input[@id='page']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('value')
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//tr[@bgcolor='#E6E6E6'][last()]/td/a").get_attribute('href')[-30:]
        driver.find_element_by_xpath("//input[@id='page']").clear()
        driver.find_element_by_xpath("//input[@id='page']").send_keys(num, Keys.ENTER)
        time.sleep(1)

        locator = (By.XPATH, "//tr[@bgcolor='#E6E6E6'][last()]/td/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('tr', attrs={'bgcolor':'#E6E6E6'})
    for tr in lis:
        a = tr.find('a')
        a.span.extract()
        try:
            name = a['title']
        except:
            name = a.text.strip()
        tr.a.extract()
        ggstart_time = tr.text.strip()
        ggstart_time = re.findall(r'([0-9]{4}-[0-9]{,2}-[0-9]{,2})', ggstart_time)[0]
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://bhzb.baosteelbidding.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//tr[@bgcolor='#E6E6E6'][last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//form[@id='pageFrm']/table/tbody/tr/td[last()]")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = int(re.findall(r'(\d+)', page)[-1])
    num = ceil(num/10)
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@border='1'][string-length()>30] | //div[@id='ef_region_inqu']")
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
    div = soup.find('table', attrs={'border':"1"})
    if div == None:
        div = soup.find('div', id='ef_region_inqu')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_gqita_yugao_hwgnzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=2050",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],

    ["jqita_zhaobiao_hwgnzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=2010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],

    ["jqita_biangeng_hwgnzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=2020",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],

    ["jqita_zhongbiaohx_hwgnzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=2030",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],

    ["jqita_zhongbiao_hwgnzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=2040",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],
    ######
    ["jqita_gqita_yugao_hwgjzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=1050",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国际招标'}), f2],

    ["jqita_zhaobiao_hwgjzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=1010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国际招标'}), f2],

    ["jqita_biangeng_hwgjzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=1020",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国际招标'}), f2],

    ["jqita_zhongbiao_hwgjzb_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=1040",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国际招标'}), f2],
    ####
    ["gcjs_gqita_yugao_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=3050",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],

    ["gcjs_zhaobiao_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=3010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],

    ["gcjs_biangeng_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=3020",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],

    ["gcjs_zhongbiaohx_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=3030",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],

    ["gcjs_zhongbiao_gg",
     "http://bhzb.baosteelbidding.com/ebsbulletin/DispatchAction.do?efFormEname=PYBF2002&type=3040",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物国内招标'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="上海宝华国际招标有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_baosteelbidding_com"], )

    #
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


