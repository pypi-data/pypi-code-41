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
from zlsrc.util.etl import est_tbs, est_meta, est_html,  add_info



def f1(driver, num):
    locator = (By.XPATH, '//table[@class="table2"]//table[@width="96%"][last()]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=page=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//table[@class="table2"]//table[@width="96%"][last()]//tr[1]//a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//table[@class="table2"]//table[@width="96%"][last()]//tr[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='table2').find_all('table',width="96%")[-1]
    lis = div.find_all('tr')[:-1]

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('td',width="24%").get_text().strip('(').strip(')')
        if 'http' in href:
            href = href
        else:
            href = 'http://zfcg.nen.com.cn/' + href


        tmp = [name, ggstart_time, href]


        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="table2"]//table[@width="96%"][last()]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//select[@name="page"]/option[last()]').text

        total = int(page)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//iframe/following-sibling::table[@class="table2"][1]//table[@width="95%"][string-length()>50]')
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

    div = soup.find('iframe').find_next_sibling('table',class_='table2')


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["zfcg_zhaobiao_diqu1_gg", "http://zfcg.nen.com.cn/ZhaoBiaoList_SJnew.jsp?page=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':"省本级"}), f2],
    ["zfcg_zhongbiao_diqu1_gg", "http://zfcg.nen.com.cn/ZhongBiaoList_SJnew.jsp?page=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':"省本级"}), f2],

    ["zfcg_zhaobiao_diqu2_gg", "http://zfcg.nen.com.cn/ZhaoBiaoList_DSnew.jsp?page=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':"区县"}), f2],
    ["zfcg_zhongbiao_diqu2_gg", "http://zfcg.nen.com.cn/ZhongBiaoList_DSnew.jsp?page=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':"区县"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="辽宁省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "liaoning"], total=2, headless=True, num=1)



