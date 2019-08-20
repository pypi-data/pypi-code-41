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
    locator = (By.XPATH, "//table[@width='98%' and @cellpadding='2']/tbody/tr[last()]/td/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//td[@class='STYLE8'][1]")
    page = WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(re.findall(r'(\d+)/', page)[0])

    if num != cnum:
        val = driver.find_element_by_xpath("//table[@width='98%' and @cellpadding='2']/tbody/tr[last()]/td/span/a").get_attribute('href')[-12:]
        url = re.sub(r'pageno=[0-9]+', 'pageno=%d' % num, driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//table[@width='98%' and @cellpadding='2']/tbody/tr[last()]/td/span/a[not(contains(@href,'{}'))]".format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', attrs={'width':'98%','cellpadding':'2'}).tbody
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
            href = 'http://www.gdhualun.com.cn/' + link
        zb_num = tr.find_all('td')[0].text.strip()
        info = json.dumps({'zb_num':zb_num}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@width='98%' and @cellpadding='2']/tbody/tr[last()]/td/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='STYLE8'][1]")
    page = WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@class='STYLE8' and @valign='middle'][string-length()>30]")
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
    div = soup.find('td', attrs={'class':'STYLE8','valign':'middle'}).parent.parent
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.gdhualun.com.cn/ggxxcx.asp?mtype=1&sql=SELECT+%2A+FROM+gonggao+where+fbbz%3D1++and+type%3D1+ORDER+BY+FBRQ+DESC%2C+ID+DESC&pageno=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.gdhualun.com.cn/ggxxcx.asp?mtype=2&sql=SELECT+%2A+FROM+gonggao+where+fbbz%3D1++and+type%3D2+ORDER+BY+FBRQ+DESC%2C+ID+DESC&pageno=1",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_zhongbiao_gg",
     "http://www.gdhualun.com.cn/ggxxcx.asp?mtype=3&sql=SELECT+%2A+FROM+gonggao+where+fbbz%3D1++and+type%3D3+ORDER+BY+FBRQ+DESC%2C+ID+DESC&pageno=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bian_bu_gg",
     "http://www.gdhualun.com.cn/ggxxcx.asp?mtype=5&sql=SELECT+%2A+FROM+gonggao+where+fbbz%3D1++and+type%3D5+ORDER+BY+FBRQ+DESC%2C+ID+DESC&pageno=1",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

]

# 广东华伦招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_gdhualun_com_cn"], )


    # for d in data[1:]:
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


