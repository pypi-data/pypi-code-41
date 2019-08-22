import json
import random
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large



def f1(driver, num):
    locator = (By.XPATH, "//div[@class='cfcpn_list_content text-left'][last()]/p/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//li[@class='page active']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='cfcpn_list_content text-left'][last()]/p/a").get_attribute('href')[-12:]

        url = re.sub('pageNo=[0-9]+', 'pageNo=%d' % num, url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='cfcpn_list_content text-left'][last()]/p/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('div', class_='cfcpn_list_content text-left')
    for tr in lis:
        a = tr.find('p', class_='cfcpn_list_title').a
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('p', class_='cfcpn_list_date text-right').text.strip()
        ggstart_time = re.findall(r'发布时间：(.*)', ggstart_time)[0]
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.cfcpn.com' + link

        info = {}
        dt = tr.find('div', class_='media-body')
        dt.find('h4').extract()
        dt.find('p').extract()
        txts = dt.get_text().replace('\n', ',').replace('\xa0', '').replace(' ', '')
        txt = txts.split(',')
        inf = {}
        for ts in txt:
            if ts:
                t = ts.split(':')
                if t[1]:inf[t[0]] = t[1]
        if inf:info['info_data']=inf
        if info:info=json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='cfcpn_list_content text-left'][last()]/p/a")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//ul[@class='pagination']/li[@class='page'][last()]")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(total_page)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='news_content'][string-length()>40]")
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
    div = soup.find('div', id='news_content').parent
    return div


data = [
    ["qycg_zhaobiao_gg",
     "http://www.cfcpn.com/plist/caigou?pageNo=1&kflag=0",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qycg_biangeng_gg",
     "http://www.cfcpn.com/plist/biangeng?pageNo=1&kflag=0",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["qycg_zhongbiao_gg",
     "http://www.cfcpn.com/plist/jieguo?pageNo=1&kflag=0",
     ["name", "ggstart_time", "href", "info"],f1 ,f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="金采网", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_cfcpn_com"])

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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


