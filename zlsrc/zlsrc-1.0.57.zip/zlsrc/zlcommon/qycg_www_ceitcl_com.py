import re
from math import ceil

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time




def f1(driver, num):
    locator = (By.XPATH, "//ul[contains(@class, 'sub_news_list')]/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    locator = (By.XPATH, "//div[@class='pages']/span")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    url = driver.current_url
    if int(cnum) != int(num):
        val = driver.find_element_by_xpath("//ul[contains(@class, 'sub_news_list')]/li[last()]/a").get_attribute('href')[-25:]
        url = re.sub('page=[0-9]+', 'page=%d'% num, url)
        driver.get(url)

        locator = (By.XPATH, '//ul[contains(@class, "sub_news_list")]/li[last()]/a[not(contains(@href,"%s"))]'%(val))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    ul = soup.find('ul', class_=re.compile('sub_news_list'))
    lis = ul.find_all('li')

    for tr in lis:
        a = tr.find('a').extract()
        try:
            name = a['title']
        except:
            name = a.text.strip()

        if 'http' in a['href']:
            href = a['href']
        else:
            href = 'http://www.ceitcl.com' + a['href']
        ggstart_time = tr.text.strip()
        temp = [name, ggstart_time, href]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[contains(@class, 'sub_news_list')]/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    locator = (By.XPATH, "//a[@class='a1'][1]")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'\d+', total_page)[0]
    num = ceil(int(num)/10)
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='article_con'][string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
    div=soup.find('div',class_='article_box')
    if div == None:raise ValueError
    return div


data = [
    ["qycg_zhaobiao_gg",
     "http://www.ceitcl.com/index.php?m=content&c=index&a=lists&catid=51&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiao_gg",
     "http://www.ceitcl.com/index.php?m=content&c=index&a=lists&catid=52&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_gqita_gg",
     "http://www.ceitcl.com/index.php?m=content&c=index&a=lists&catid=53&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]




def work(conp, **args):
    est_meta(conp, data=data, diqu="中经国际招标集团有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_ceitcl_com"])

    #
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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
