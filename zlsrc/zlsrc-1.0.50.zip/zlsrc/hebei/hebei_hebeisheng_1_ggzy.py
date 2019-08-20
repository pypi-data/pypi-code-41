from pprint import pprint

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info



def f1(driver, num):
    locator = (By.XPATH, '//td[@id="tdcontent"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('Paging=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=Paging=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//td[@id="tdcontent"]//tr[1]//a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//td[@id="tdcontent"]//tr[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('td',id="tdcontent").find_all('tr')

    for tr in trs:
        href=tr.find('a')['href'].strip()
        name=tr.find('a').get_text(strip=True)
        ggstart_time=tr.find('span',class_='ewb-con-date r').get_text(strip=True)
        diqu=re.findall('^【(.+?)】',name)
        if diqu:
            info=json.dumps({'diqu':diqu[0]},ensure_ascii=False)
        else:
            info=None
        if 'http' in href:
            href = href
        else:
            href = 'http://www.hebeibidding.com' + href

        tmp = [name, ggstart_time, href,info]
        
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//td[@id="tdcontent"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//td[@class="huifont"]').text
        total=re.findall('/(\d+)',page)[0]
    except:
        total=1

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="contents"][string-length()>50]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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

    div = soup.find('div',class_="details-info")

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.hebeibidding.com/TPFront/showinfo/xmxxlist.aspx?title=&lx=001&categoryNum=016001&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://www.hebeibidding.com/TPFront/showinfo/xmxxlist.aspx?title=&lx=001&categoryNum=016002&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_cheng_da_gg", "http://www.hebeibidding.com/TPFront/showinfo/xmxxlist.aspx?title=&lx=001&categoryNum=016003&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.hebeibidding.com/TPFront/showinfo/xmxxlist.aspx?title=&lx=001&categoryNum=016004&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg", "http://www.hebeibidding.com/TPFront/showinfo/xmxxlist.aspx?title=&lx=001&categoryNum=016006&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=002&CategoryNum=016001&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=002&CategoryNum=016002&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_cheng_da_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=002&CategoryNum=016003&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=002&CategoryNum=016004&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=002&CategoryNum=016006&Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_jizhong_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=003&CategoryNum=016001&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'集中采购'}), f2],
    ["jqita_biangeng_jizhong_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=003&CategoryNum=016002&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'集中采购'}), f2],
    ["jqita_gqita_cheng_da_jizhong_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=003&CategoryNum=016003&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'集中采购'}), f2],
    ["jqita_zhongbiao_jizhong_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=003&CategoryNum=016004&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'集中采购'}), f2],

    ["jqita_zhaobiao_guoji_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=004&CategoryNum=016001&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'国际招标'}), f2],
    ["jqita_biangeng_guoji_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=004&CategoryNum=016002&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'国际招标'}), f2],
    ["jqita_zhongbiao_guoji_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=004&CategoryNum=016004&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'国际招标'}), f2],

    ["jqita_zhaobiao_lingxing_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=005&CategoryNum=016001&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'零星招标'}), f2],
    ["jqita_biangeng_lingxing_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=005&CategoryNum=016002&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'零星招标'}), f2],
    ["jqita_zhongbiao_lingxing_gg", "http://www.hebeibidding.com/TPFront//showinfo/xmxxlist.aspx?title=&lx=005&CategoryNum=016004&Paging=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'零星招标'}), f2],



]

# pprint(data)



def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hebei"], total=2, headless=True, num=1)
    pass


