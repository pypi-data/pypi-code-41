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
    locator = (By.XPATH, "//ul[@class='pag_zbList']/li[last()]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//span[@class='page']")
    page = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(page)

    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='pag_zbList']/li[last()]/a").get_attribute('href')[-15:]

        url = re.sub(r'p=[0-9]+', 'p=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='pag_zbList']/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='pag_zbList')
    lis = div.find_all('li', recursive=False)
    for tr in lis:
        a = tr.find('a')
        name = tr.find('div', class_='index_zbL2').text.strip()
        ggstart_time = tr.find('div', class_='index_zbL3').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.bkpmzb.com/bidding/' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='pag_zbList']/li[last()]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='pages']/a[last()]")
    page = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')
    num = re.findall(r'p=([0-9]+)', page)[0]

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='news_box0_minfo'][string-length()>100]")
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
    div = soup.find('div', class_='news_box0_minfo').parent
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.bkpmzb.com/bidding/list.php?oid=257&p=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_liu_bian_gg",
     "http://www.bkpmzb.com/bidding/list.php?oid=265&p=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.bkpmzb.com/bidding/list.php?oid=264&p=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


##北京科技园拍卖招标有限公司

def work(conp, **args):
    est_meta(conp, data=data, diqu="北京科技园拍卖招标有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_shbtpm_com"])

    #
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
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


