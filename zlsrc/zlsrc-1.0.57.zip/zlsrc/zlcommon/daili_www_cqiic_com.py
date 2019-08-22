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
    locator = (By.XPATH, "//table[@id='moreinfo_zbgg1_DataGrid1']/tbody/tr[last()]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//td[@class='huifont']")
    page = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(re.findall(r'([0-9]+)/', page)[0])

    if num != cnum:
        val = driver.find_element_by_xpath("//table[@id='moreinfo_zbgg1_DataGrid1']/tbody/tr[last()]//a").get_attribute('href')[-30:]

        url = re.sub(r'Paging=[0-9]+', 'Paging=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//table[@id='moreinfo_zbgg1_DataGrid1']/tbody/tr[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='moreinfo_zbgg1_DataGrid1').tbody
    lis = div.find_all('tr', recursive=False)
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='r').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.cqiic.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@id='moreinfo_zbgg1_DataGrid1']/tbody/tr[last()]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//td[@class='huifont']")
    page = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/([0-9]+)', page)[0]

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@id='TDContent'][string-length()>100]")
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
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.cqiic.com/CZJTweb/ShowInfo/jyzxmore.aspx?CategoryNum=005001&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bian_bu_gg",
     "http://www.cqiic.com/CZJTweb/ShowInfo/jyzxmore.aspx?CategoryNum=005002&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.cqiic.com/CZJTweb/ShowInfo/jyzxmore.aspx?CategoryNum=005004&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆国际投资咨询集团有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_cqiic_com"])

    #
    # for d in data[-6:]:
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
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


