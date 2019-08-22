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
    locator = (By.XPATH, "//div[@class='jianjie']/table/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//font[@color='#FF0000'][2]")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='jianjie']/table/tbody/tr[last()]//a").get_attribute('href')[-12:]
        url = re.sub('page=[0-9]+', 'page=%d' % num, url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='jianjie']/table/tbody/tr[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='jianjie').table.tbody
    lis = div.find_all('tr')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()

        if tr.find('td', style=re.compile('font-size:12px;')):
            ggstart_time = tr.find('td', style=re.compile('font-size:12px;')).text.strip()
            if re.findall(r'\[(.*)\]', ggstart_time):
                ggstart_time = re.findall(r'\[(.*)\]', ggstart_time)[0]
            else:ggstart_time='-'
        else:
            ggstart_time='-'


        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.tsjj.com.cn/' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='jianjie']/table/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//font[@color='#FF0000'][2]")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@colspan='3'][string-length()>60]")
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
    div = soup.find('div', class_='jianjie')
    return div


data = [

    ["gcjs_zhaobiao_gg",
     "http://www.tsjj.com.cn/zbgg.asp?upid=105&typeid=105&t=4&page=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["gcjs_zhongbiao_gg",
     "http://www.tsjj.com.cn/Nouvelles.asp?upid=106&typeid=106&t=4&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="天津市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_tsjj_com_cn"])


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


