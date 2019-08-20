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
    locator = (By.XPATH, "//div[@class='Crd_2']/ul[last()]/li/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//span[@class='count']")
    page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(re.findall(r'(\d+)', page)[0])


    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='Crd_2']/ul[last()]/li/a").get_attribute('href')[-10:]

        url = re.sub(r'page=[0-9]+', 'page=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='Crd_2']/ul[last()]/li/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='Crd_2')
    lis = div.find_all('ul', recursive=False)
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('li', class_='time').text.strip('[]')
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.tjjszb.com/' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='Crd_2']/ul[last()]/li/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//span[@class='count']")
    page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'(\d+)', page)[-1]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='Cr'][string-length()>10]")
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
    div1 = soup.find('div', class_='Cr')

    if div1.find('a'):
        link = div1.find('a')['href']
        driver.get(link)
        locator = (By.XPATH, "//div[@class='body'][string-length()>100]")
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
        div2 = soup.find('div', class_='body')
    else:div2 = ''
    div = str(div1)+str(div2)
    div = BeautifulSoup(div, 'html.parser')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.tjjszb.com/zbywo.asp?id=%D5%D0%B1%EA%B9%AB%B8%E6&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 天津市建设工程招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="天津市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest", "tianjin_tianjinshi_daili"],add_ip_flag=True)


    # for d in data:
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
    #     df=f1(driver, 11)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


