import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, est_meta




def f1(driver, num):
    locator = (By.XPATH, "//tr[@height='30'][last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//font[@color='red']/b")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//tr[@height='30'][last()]//a").get_attribute('href')[-30:]
        if '?Paging' not in url:
            s = 'Paging=%d'% num if num>1 else 'Paging=1'
            url+=s
        elif num == 1:
            url = re.sub('Paging=[0-9]+', 'Paging=1', url)
        else:
            s = 'Paging=%d' % num if num > 1 else 'Paging=1'
            url = re.sub('Paging=[0-9]+', s, url)
        driver.get(url)
        locator = (By.XPATH, "//tr[@height='30'][last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', id='right').table.tbody
    lis = table.find_all('tr', height='30', recursive=False)
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('td', class_='infodate').text.strip()
        href = 'http://glzjw.glin.cn:8213'+a['href']

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//tr[@height='30'][last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//font[@color='blue'][last()]/b")
    total_num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    driver.quit()
    return int(total_num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[contains(@id, 'TDContent')][string-length()>100]")
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
    div = soup.find('table', id='tblInfo')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://glzjw.glin.cn:8213/glzj/zbz/029004/?Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省桂林市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_guangxi_guilin"])


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


