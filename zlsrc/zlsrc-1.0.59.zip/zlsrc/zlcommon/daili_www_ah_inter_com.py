import random
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='list_news']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//span[@class='current']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='list_news']/li[last()]/a").get_attribute('href')[-15:]

        url = re.sub('page=[0-9]+', 'page=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='list_news']/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='list_news')
    lis = div.find_all('li')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.ah-inter.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='viciao']/a[last()]")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')
    page = re.findall(r'page=(\d+)', total_page)[0]
    driver.quit()
    return int(page)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content'][string-length()>50]")
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
    div = soup.find('div', id='zbmeno')
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.ah-inter.com/SkimBidding.asp?BidType=9&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_gg",
     "http://www.ah-inter.com/SkimBidding.asp?BidType=10&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '招标预告'}), f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.ah-inter.com/SkimBidding.asp?BidType=11&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.ah-inter.com/SkimBidding.asp?BidType=12&page=1",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_gqita_bian_da_gg",
     "http://www.ah-inter.com/SkimBidding.asp?BidType=13&page=1",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_zhaobiao_xunjia_gg",
     "http://www.ah-inter.com/SkimBidding.asp?BidType=37&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '询价'}), f2],
]



def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省招标集团股份有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_ah_inter_com"])


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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


