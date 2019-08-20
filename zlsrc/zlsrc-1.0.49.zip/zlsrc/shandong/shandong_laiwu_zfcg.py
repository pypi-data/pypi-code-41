import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zlsrc.util.etl import est_meta, est_html,add_info



def f1(driver, num):

    locator = (By.XPATH, '(//td[@class="Font9"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url

    cnum = re.findall('curpage=(\d+)&', url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('(//td[@class="Font9"])[1]/a').get_attribute('href').rsplit(
            '/', maxsplit=1)[1]

        s = 'curpage=%d&' % num
        url_ = re.sub('curpage=(\d+)&', s, url)
        driver.get(url_)

        locator = (By.XPATH, '(//td[@class="Font9"])[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find_all('td', class_='Font9')[:-1]
    for td in div:
        if len(td) == 0 :
            continue
        href = td.a['href']
        if 'http' in href:
            href = href
        else:
            href = "http://zfcg.laiwu.gov.cn" + href
        name = td.a['title']

        td.a.extract()

        ggstart_time = td.get_text().strip()
        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, '(//td[@class="Font9"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('(//td[@class="Font9"])[last()]//strong').text

    total = re.findall('/(\d+)', page)[0]
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '(//td[@bgcolor="#FFFFFF"])[3][string-length()>50]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    try:
        rame = driver.find_element_by_xpath('//td[@class="aa"]/iframe')
        driver.switch_to.frame(rame)
        locator = (By.XPATH, '//body[string-length()>100]')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        mark = 0
    except:
        mark = 1

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

    driver.switch_to.default_content()

    if mark == 1:
        div = soup.find_all('td', attrs={'bgcolor': '#FFFFFF'})[2].parent.parent

    else:
        div1 = soup.find('body')
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div2 = soup.find_all('td', attrs={'bgcolor': '#FFFFFF'})[2].parent.parent
        div = BeautifulSoup(str(div1) + str(div2), 'html.parser')

    if div == None:
        raise ValueError('div is None')

    return div

data = [


    ["zfcg_zhaobiao_diqu1_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=0301&subject=&pdate=",["name","ggstart_time", "href", 'info'], add_info(f1,{'diqu':"市本级"}), f2],
    ["zfcg_zhongbiao_diqu1_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=0302&subject=&pdate=",["name","ggstart_time", "href", 'info'], add_info(f1,{'diqu':"市本级"}), f2],
    ["zfcg_zhaobiao_diqu2_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=0303&subject=&pdate=",["name","ggstart_time", "href", 'info'], add_info(f1,{'diqu':"区县"}), f2],
    ["zfcg_zhongbiao_diqu2_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=0304&subject=&pdate=",["name","ggstart_time", "href", 'info'],add_info(f1,{'diqu':"区县"}), f2],

    ["zfcg_biangeng_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=0305&subject=&pdate=",["name","ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_liubiao_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=0306&subject=&pdate=",["name","ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_zgys_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=0307&subject=&pdate=",["name","ggstart_time", "href", 'info'], f1, f2],

    ["zfcg_yucai_diqu1_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/listneedall.jsp?curpage=1&subject=&pdate=&unitname=",["name","ggstart_time", "href", 'info'], add_info(f1,{'diqu':"市本级"}), f2],
    ["zfcg_yucai_diqu2_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=2504&subject=&pdate=",["name","ggstart_time", "href", 'info'], add_info(f1,{'diqu':"区县"}), f2],
    ["zfcg_yanshou_diqu2_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=2506&subject=&pdate=",["name","ggstart_time", "href", 'info'], add_info(f1,{'diqu':"区县"}), f2],
    ["zfcg_yanshou_diqu1_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/listchkall.jsp?curpage=1&subject=&pdate=&unitname=",["name","ggstart_time", "href", 'info'],add_info(f1,{'diqu':"市本级"}), f2],
    ["zfcg_yucai_diqu3_gg", "http://zfcg.laiwu.gov.cn/sdgp2014/site/channelall.jsp?curpage=1&colcode=2509&subject=&pdate=",["name","ggstart_time", "href", 'info'], add_info(f1,{'tag':'其他'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省莱芜市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch", "shandong_laiwu"]

    work(conp=conp,headless=False,num=1,cdc_total=1)