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
    locator = (By.XPATH, "//table[@width='92%']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//select[@name='page']/option[@selected]")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(page)

    if num != cnum:
        val = driver.find_element_by_xpath("//table[@width='92%']/tbody/tr[last()]//a").get_attribute('href')[-15:]
        Select(driver.find_element_by_xpath("//select[@name='page']")).select_by_visible_text('%d'% num)
        time.sleep(1)
        driver.find_element_by_xpath('//td[@align="right"]/input[last()]').click()
        locator = (By.XPATH, "//table[@width='92%']/tbody/tr[last()]//a[not(contains(@href,'{}'))]".format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', width='92%').tbody
    lis = table.find_all('tr')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()

        ggstart_time = tr.find_all('td')[-1].font.text.strip()
        ggstart_time = re.findall(r'\[(.*)\]', ggstart_time)[0]

        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.ahgljl.com/' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@width='92%']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//select[@name='page']/option[last()]")
    num = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//table[@width='94%'][string-length()>50]")
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
    div = soup.find('td', height="846")
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.ahgljl.com/news.asp?typeid=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.ahgljl.com/news.asp?typeid=9",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


# 安徽省公路工程建设监理有限责任公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_ahgljl_com"], )

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


