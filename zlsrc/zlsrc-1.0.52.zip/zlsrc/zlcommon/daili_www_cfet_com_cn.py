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
    locator = (By.XPATH, "//div[@class='ny_zb_list']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//span[@class='current']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='ny_zb_list']/ul/li[last()]/a").get_attribute('href')[-20:]
        url = re.sub('p=[0-9]+', 'p=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='ny_zb_list']/ul/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='ny_zb_list').ul
    lis = table.find_all('li')
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
            href = 'http://www.cfet.com.cn' + link
        info = {}
        if 'www.chinabidding.cn' in href:
            info['hreftype']='不可抓网页'
            info= json.dumps(info, ensure_ascii=False)
        else:info= None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='ny_zb_list']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='pagination']/ul/li[last()-2]")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(page)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='ArticleContent'][string-length()>60] | //div[@class='table'][string-length()>60] | //div[@class='as-article'][string-length()>30]")
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
    div = soup.find('div', class_='ny_zb_con')
    if div == None:
        div = soup.find('div', class_='vF_detail_main')
        if div == None:
            div = soup.find('div', class_='as-article')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.cfet.com.cn/index.php?g=portal&m=list&a=index&id=33&p=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.cfet.com.cn/index.php?g=portal&m=list&a=index&id=34&p=1",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_biangeng_gg",
     "http://www.cfet.com.cn/index.php?g=portal&m=list&a=index&id=36&p=1",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

]

##中国远东国际招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="中国远东国际招标有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_cfet_com_cn"], )


    # for d in data[-1:]:
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


