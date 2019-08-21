import json
import random
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info




def f1(driver, num):
    locator = (By.XPATH, "//table[contains(@class, 'table')]/tbody/tr[last()]/td[2]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//p[@id='pages']/b[2]")
        page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'([0-9]+)/', page)[0])
    except:cnum=1

    if num != cnum:
        val = driver.find_element_by_xpath("//table[contains(@class, 'table')]/tbody/tr[last()]/td[2]/a").get_attribute('href')[-12:]

        url = re.sub(r'page=[0-9]+', 'page=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//table[contains(@class, 'table')]/tbody/tr[last()]/td[2]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_=re.compile('table')).tbody
    lis = div.find_all('tr', recursive=False)
    for tr in lis[1:]:
        a = tr.find_all('a')[-1]
        try:
            name = a['title']
        except:
            name = a.text.strip()

        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.jxbidding.com/' + link

        info = {}
        if 'catid=154' in url:
            ggstart_time = tr.find_all('td')[-1].text.strip()
            zhongbdw = tr.find_all('td')[-2].text.strip()
            if zhongbdw:info['zhongbdw']=zhongbdw
            zbbh = tr.find_all('a')[0].text.strip()
            if zbbh:info['zbbh']=zbbh
        elif 'catid=146' in url or 'catid=167' in url:
            ggstart_time = tr.find_all('td')[-2].text.strip()
            zblx = tr.find_all('td')[-3].text.strip()
            if zblx:info['zblx']=zblx
            zbbh = tr.find_all('a')[0].text.strip()
            if zbbh:info['zbbh']=zbbh
            kb_time = tr.find_all('td')[-1].text.strip()
            if kb_time:info['kb_time']=kb_time
        else:raise ValueError('链接错误')
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//table[contains(@class, 'table')]/tbody/tr[last()]/td[2]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//p[@id='pages']/b[2]")
        page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/([0-9]+)', page)[0]
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='endtext'][string-length()>100]")
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
    div = soup.find('div', id='content')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.jxbidding.com/list.php?catid=146&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bian_cheng_gg",
     "http://www.jxbidding.com/list.php?catid=167&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.jxbidding.com/list.php?catid=154&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 江西省机电设备招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="江西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "jiangxi_jiangxisheng_daili"])

    #
    # for d in data[1:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #
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


