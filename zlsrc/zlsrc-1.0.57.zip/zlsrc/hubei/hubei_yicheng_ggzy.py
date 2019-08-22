import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, est_meta_large, est_meta


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="work-one-list"][1]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if 'index.html' in url:
        cnum=1
    else:
        cnum=int(re.findall('index_(\d+).html',url)[0])

    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="work-one-list"][1]/ul/li[1]/a').get_attribute('href')[-20:]

        if num ==1:
            url=re.sub('index_\d+.html','index.html',url)
        else:
            url = re.sub('index_*\d*.html','index_%s.html'%(num-1), url)

        driver.get(url)
        locator = (By.XPATH, "//div[@class='work-one-list'][1]/ul/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='zhengce-one-bot-list')
    lis = table.find_all('li')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.get_text(strip=True)

        ggstart_time = tr.find('span').text.strip('[').strip(']')

        href = url.rsplit('/',maxsplit=1)[0]+a['href'].strip('.')
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, '//div[@class="work-one-list"][1]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=re.findall('createPageHTML\((\d+),',driver.page_source)[0]

    driver.quit()
    return int(total)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="xqym-p"][string-length()>50]')
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
    div = soup.find('div', class_='xqym')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://yc.xiangyang.gov.cn/ggzyjyzx/zbgg/index.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ####
    ["gcjs_zhongbiao_gg",
     "http://yc.xiangyang.gov.cn/ggzyjyzx/zbgs/jsgcl/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://yc.xiangyang.gov.cn/ggzyjyzx/zbgs/zfcgl/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ####
    ["zfcg_gqita_zhao_bian_gg",
     "http://yc.xiangyang.gov.cn/ggzyjyzx/zfcg/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省宜城市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_hubei_yicheng"],num=1)


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    driver=webdriver.Chrome()
    driver.get('http://yc.xiangyang.gov.cn/ggzyjyzx/zbgg/index.html')
    f1(driver,2)
    # df=f1(driver, 2)
    # print(df.values)

    # for f in df[2].values:
    #     d = f3(driver, f)
    #     print(d)


