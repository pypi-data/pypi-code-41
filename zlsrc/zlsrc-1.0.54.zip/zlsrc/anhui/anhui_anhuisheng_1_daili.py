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
    locator = (By.XPATH, "//ul[@class='bidding-list']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//li[@class='active']/a")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='bidding-list']/li[last()]/a").get_attribute('href')[-10:]
        url = re.sub(r'pageIndex=[0-9]+', 'pageIndex=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='bidding-list']/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('ul', class_='bidding-list')
    lis = table.find_all('li')
    url = driver.current_url
    for tr in lis[1:]:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.find('span', class_='text').text.strip()
        try:
            ggstart_time = tr.find('span', class_='publishtime').text.strip()
            ggstart_time = re.findall(r'[0-9]{4}/[0-9]{,2}/[0-9]{,2}', ggstart_time)[0]
        except:
            ggstart_time = tr.find('span', class_='countDown')['data-endtime']
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'https://www.ahbidding.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='bidding-list']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        page = driver.find_element_by_xpath("//ul[@class='pagination']/li[last()]/a").get_attribute('href')
        num = re.findall(r'pageIndex=(\d+)', page)[0]
    except:num=1

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@class, 'details-text')][string-length()>100]")
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
    div = soup.find('div', class_='details-text').find('div', class_='project-content', style='display: block;')

    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_gqita_zbygg_gg",
     "https://www.ahbidding.com/BidNotice/zbcgxx/zbygg?pageIndex=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'招标预公告'}), f2],

    ["jqita_zhaobiao_gg",
     "https://www.ahbidding.com/BidNotice/zbcgxx/zgcggg?pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_biangeng_gg",
     "https://www.ahbidding.com/BidNotice/zbcgxx/bggg?pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["jqita_zhongbiaohx_gg",
     "https://www.ahbidding.com/BidNotice/zbcgxx/zbhxrgs?pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "https://www.ahbidding.com/BidNotice/zbcgxx/zbjggg?pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 信e采
def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_ahbidding_com"], )


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


