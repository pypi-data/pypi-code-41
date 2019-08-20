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
    locator = (By.XPATH, "//div[@id='list']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//div[@class='page']/select/option[@selected='selected']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@id='list']/ul/li[last()]/a").get_attribute('href')[-12:]

        Select(driver.find_element_by_xpath("//div[@class='page']/select")).select_by_value("{}".format(num))
        time.sleep(1)

        locator = (By.XPATH, "//div[@id='list']/ul/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('div', id='list').ul
    divs = lis.find_all('li', recursive=False)
    for tr in divs:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.sdtender.com/' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@id='list']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='page']/select/option[last()]")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(page)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='newtext'][string-length()>60]")
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
    div = soup.find('div', class_='newtext').parent
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.sdtender.com/list.asp?id=139&p=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["jqita_zhongbiao_gg",
     "http://www.sdtender.com/list.asp?id=140&p=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 山东招标股份有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_sdtender_com"])


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


