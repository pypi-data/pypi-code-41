import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_meta,est_html




def f1(driver, num):
    locator = (By.XPATH, "//div[@class='cate_right']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//ul[@class='pagination']/li[1]/span")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(re.findall(r'第(\d+)页', snum)[0])

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='cate_right']/ul/li[1]/a").get_attribute('href')[-20:]
        s = 'page=%d' % num if num>1 else 'page=1'
        url = re.sub('page=[0-9]+', s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='cate_right']/ul/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='cate_right').ul
    lis = div.find_all('li')
    for tr in lis:
        a = tr.find('a')
        name = a.span.text.strip()
        ggstart_time = a.time.text.strip()
        href = a['href']
        if 'http' in href:
            href = href
        else:
            href = 'http://www.gzsjj.com' + href
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='cate_right']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//ul[@class='pagination']/li[1]/span")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'共(\d+)页', snum)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='cate_right'][string-length()>40]")
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
    div = soup.find('div', class_='cate_right')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.gzsjj.com/index/tender/index/cid/3.html?page=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["gcjs_zhongbiao_gg",
     "http://www.gzsjj.com/index/ztender/index/cid/4.html?page=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="贵州省",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlsrc","guizhousheng"])

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

