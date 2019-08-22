import pandas as pd
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='contain1' and @style='display: block;']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    before = len(driver.page_source)
    time.sleep(0.1)
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
    div = soup.find('div', attr={'class': 'contain1', 'style': 'display: block;'})
    return div


def f1(driver, num):
    try:
        time.sleep(1)
        locator = (By.XPATH, "//ul[@id='searchid']/li[1]/span/a")
        val = WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator)).get_attribute("href")[-40:]
    except:
        time.sleep(2)
        locator = (By.XPATH, "//ul[@id='searchid']/li[1]/span/a")
        val = WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator)).get_attribute("href")[-40:]
    cnum = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//span[@id='pageIndex']"))).text
    val2 = val
    c = 10
    if int(cnum) != int(num):
        while val == val2 and c > 0:
            # driver.refresh()
            js = "changePage($('#titles').val(),$('#choose').val(),$('#projectType').val(),$('#zbCode').val(),$('#appcode').val(),%s, page.rows)" % num
            driver.execute_script(js)

            try:
                time.sleep(1)
                locator = (By.XPATH, "//ul[@id='searchid']/li[1]/span/a")
                val2 = WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator)).get_attribute("href")[-40:]
            except:
                time.sleep(2)
                locator = (By.XPATH, "//ul[@id='searchid']/li[1]/span/a")
                val2 = WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator)).get_attribute("href")[-40:]
            c -= 1
            locator = (By.XPATH, '//ul[@id="searchid"]/li[1]/span/a[not(contains(@href,"%s"))]' % val)
            # locator = (By.XPATH,'//div[@class="progressbar-text"]')
            WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))
            # ele = driver.find_element_by_xpath('//div[@class="progressbar-text"]')
    if val2 == val: raise ValueError('翻页失败')
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@id='searchid']/li")
    for content in content_list:
        name = content.xpath("./span/a/text()")[0].strip()
        ggstart_time = content.xpath('./span[2]/text()')[0].strip().strip('[').strip(']').strip()
        url = content.xpath("./span/a/@href")[0].split('/', maxsplit=1)[-1]
        href = "http://www.zfcg.suzhou.gov.cn/" + url
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_temp, count = '', 5
    locator = (By.XPATH, "//span[@id='totalPage']")
    while total_temp == '':
        count -= 1
        if count < 0: break
        total_temp = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
        time.sleep(count / 5)
    total_page = int(WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text)

    driver.quit()
    return int(total_page)


data = [
    # #
    ["zfcg_zhaobiao_gg",
     "http://www.zfcg.suzhou.gov.cn/html/search.shtml?title=&choose=&projectType=0&zbCode=&appcode=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.zfcg.suzhou.gov.cn/html/search.shtml?title=&choose=&projectType=1&zbCode=&appcode=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.zfcg.suzhou.gov.cn/html/search.shtml?title=&choose=&projectType=2&zbCode=&appcode=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省苏州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_suzhou"])

    # driver =webdriver.Chrome()
    # driver.get('http://www.zfcg.suzhou.gov.cn/html/search.shtml?title=&choose=&projectType=0&zbCode=&appcode=')
    # for i in range(1,10):
    #     f1(driver,i)

    # print(f3(driver, 'http://www.zfcg.suzhou.gov.cn/html/project/20190411110900041.shtml'))
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     for i in range(1, total):
    #         # i =  random.randint(1,total)
    #         driver.get(d[1])
    #         print(d[1])
    #         df_list = f1(driver, i).values.tolist()
    #         print(df_list[:10])
    #         df1 = random.choice(df_list)
    #         print(str(f3(driver, df1[2]))[:100])
    #         driver.quit()
