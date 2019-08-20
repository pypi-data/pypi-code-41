
import pandas as pd
import re
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
    locator = (By.XPATH, "//div[@class='sublanmu_box sublanmu_box_647']")
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
    div = soup.find('div', class_="sublanmu_box sublanmu_box_647")
    return div


def f1(driver, num):
    try:
        locator = (By.XPATH, '//ul[@class="open_list"]/li/a')
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]
    except:
        driver.refresh()
        locator = (By.XPATH, '//ul[@class="open_list"]/li/a')
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]
    locator = (By.XPATH, '//div[@class="pagesite"]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)\/',txt)[0]
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub('index[_\d]*', 'index_' + str(num), url, count=1)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="open_list"]/li/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="open_list"]/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = 'http://www.tangshan.gov.cn' + content.xpath("./a/@href")[0]

        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] =None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="pagesite"]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)',txt)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg",
     "http://www.tangshan.gov.cn/zhuzhan/rmzfzhaobiaogonggao/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.tangshan.gov.cn/zhuzhan/rmzfzhongbiaogonggao/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="河北省唐山市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "hebei_tangshan"])
    # driver =webdriver.Chrome()
    # url = "http://www.tangshan.gov.cn/zhuzhan/rmzfzhaobiaogonggao/index.html"
    # driver.get(url)
    # f1(driver,2)
    # f1(driver,4)
    # print(f2(driver))
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     tota = f2(driver)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     for i in range(1,tota):
    #         print(i)
    #         df_list = f1(driver,i).values.tolist()
    #         print(df_list)
    #         df1 = random.choice(df_list)
    #         # print(f3(driver, df1[2]))
    #         driver.get(d[1])