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
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//table[@class='table1']/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//table[@class='fy']/tbody//strong/font")
    page = WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(page)

    if num != cnum:
        val = driver.find_element_by_xpath("//table[@class='table1']/tbody/tr[last()]/td/a").get_attribute('href')[-12:]
        url = re.sub(r'page=[0-9]+', 'page=%d' % num, driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//table[@class='table1']/tbody/tr[last()]/td/a[not(contains(@href,'{}'))]".format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='table1').tbody
    lis = table.find_all('tr', recursive=False)
    for tr in lis[1:]:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()

        ggstart_time = tr.find_all('td')[-1].text.strip()

        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.zhongdaguoxin.com/' + link
        xm_num = tr.find_all('td')[0].text.strip()
        info = json.dumps({'xm_num':xm_num}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@class='table1']/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//select[@name='page']/option[last()]")
    num = WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).get_attribute('value')
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='Rep'][string-length()>30]")
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
    div = soup.find('div', class_='Rep').parent
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.zhongdaguoxin.com/Article.asp?ColumnId=253&NewsTypeId=254&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.zhongdaguoxin.com/Article.asp?ColumnId=253&NewsTypeId=255&page=2",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

]

#中大国信工程管理有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="中大国信工程管理有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_zhongdaguoxin_com"], )


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


