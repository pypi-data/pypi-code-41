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
    locator = (By.XPATH, "//div[@class='content']/ul[last()]/dd//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//span[@class='current']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='content']/ul[last()]/dd//a").get_attribute('href')[-12:]

        url = re.sub(r'/p/[0-9]+', '/p/%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='content']/ul[last()]/dd//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='content')
    lis = div.find_all('ul', recursive=False)
    for tr in lis:
        a = tr.find('dd').find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('dl').span.text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.guofazhaobiao.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='content']/ul[last()]/dd//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='digg']")
        page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/([0-9]+)', page)[0]
    except:num=1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content'][string-length()>100]")
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
    div = soup.find('div', class_='wen')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.guofazhaobiao.com/index.php/Index/news_list_gg/p/1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.guofazhaobiao.com/index.php/Index/news_list_jg/p/1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

#宜国发项目管理有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="宜国发项目管理有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_guofazhaobiao_com"])

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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


