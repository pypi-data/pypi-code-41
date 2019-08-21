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
    locator = (By.XPATH, "//ul[@class='newslist']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    try:
        locator = (By.XPATH, "//a[@class='on']")
        snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(snum)
    except:cnum = 1
    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='newslist']/li[last()]/a").get_attribute('href')[-12:]

        driver.execute_script("Getpage({})".format(num))

        locator = (By.XPATH, "//ul[@class='newslist']/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('ul', class_='newslist')
    lis = table.find_all('li')
    for tr in lis:
        a = tr.find('a')

        name = tr.find('span', class_=re.compile('span1')).text.strip()
        ggstart_time = tr.find('span', class_=re.compile('span2')).text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.kmjl.cc' + link

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='newslist']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    while True:
        val = driver.find_element_by_xpath("//ul[@class='newslist']/li[last()]/a").get_attribute('href')[-12:]
        try:
            tnum = int(driver.find_element_by_xpath("//a[@class='on']").text.strip())
        except:
            break
        locator = (By.XPATH, "//div[@class='compage']/a[contains(string(), '下一页')]")
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).click()
        try:
            locator = (By.XPATH, "//ul[@class='newslist']/li[last()]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
        except:
            snum = int(driver.find_element_by_xpath("//a[@class='on']").text.strip())
            if tnum == snum:
                break
            else:raise ValueError
    try:
        num = driver.find_element_by_xpath("//a[@class='on']").text.strip()
    except:num =1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='lh26 c0'][string-length()>60]")
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
    div = soup.find('div', class_='zicontent')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.kmjl.cc/training/list-89-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_biangeng_gg",
     "http://www.kmjl.cc/training/list-97-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.kmjl.cc/news/list-98-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.kmjl.cc/training/list-99-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_liubiao_gg",
     "http://www.kmjl.cc/training/list-100-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

#昆明建设咨询监理有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="昆明建设咨询监理有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_kmjl_cc"], )


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
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


