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
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='tylist']/li[@class='on'][last()]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//a[@class='on']")
    page = WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(page)

    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='tylist']/li[@class='on'][last()]/a").get_attribute('href')[-15:]
        if '_' not in driver.current_url:
            s = '_%d.html' % num if num >1 else '.html'
            url=re.sub(r'\.html', s, driver.current_url)
        elif num == 1:
            url=re.sub(r'_(\d+)\.html', '.html' % num, driver.current_url)
        else:
            s = '_%d.html' % num if num > 1 else '.html'
            url = re.sub(r'_(\d+)\.html', s, driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='tylist']/li[@class='on'][last()]/a[not(contains(@href,'{}'))]".format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('ul', class_='tylist')
    lis = table.find_all('li', class_='on')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()

        ggstart_time = tr.find('span', class_='time').text.strip()

        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.cnszh.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='tylist']/li[@class='on'][last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@id='pages']/a[last()]")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')
    num = re.findall(r'_(\d+)\.html', page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='content'][string-length()>10]")
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
    div = soup.find('div', id="Article")
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.cnszh.com/Services/21142418.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_zhong_liu_gg",
     "http://www.cnszh.com/Services/21152418.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bian_bu_gg",
     "http://www.cnszh.com/Services/21132418.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


# 云南山重建设工程招标咨询有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="云南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_cnszh_com"], )


    # for d in data[2:]:
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


