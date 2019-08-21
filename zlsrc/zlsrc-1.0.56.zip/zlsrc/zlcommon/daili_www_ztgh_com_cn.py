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
    locator = (By.XPATH, "//ul[@id='news']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall(r'PageNo=(\d+)', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@id='news']/li[last()]//a").get_attribute('href')[-12:]
        url = re.sub('PageNo=[0-9]+', 'PageNo=%d' % num, url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@id='news']/li[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', id='news')
    lis = div.find_all('li')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='aOrange mL10').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.ztgh.com.cn' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='paglist']/a[last()]")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
    num = re.findall(r'PageNo=(\d+)', total_page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@class='content'][string-length()>60]")
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
    div = soup.find('div', class_='east')
    return div


data = [

    ["jqita_zhaobiao_gg",
     "http://www.ztgh.com.cn/plus/list.php?tid=21&TotalResult=741&PageNo=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["jqita_zhongbiao_gg",
     "http://www.ztgh.com.cn/plus/list.php?tid=22&TotalResult=739&PageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

##北京中天国宏招标代理有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="北京中天国宏招标代理有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_ztgh_com_cn"])


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


