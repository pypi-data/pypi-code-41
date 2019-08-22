import random
import re
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import  est_meta, est_html, add_info
import requests
import time





def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='contentShow']")
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
    div = soup.find('div',class_='contentShow')
    return div

def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='item lh jt_dott f14']/li[1]/a")
    val = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator)).get_attribute('href')[50:]

    locator = (By.XPATH, "//div[@class='pagination_index_num currentIndex']")
    cnum = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator)).text

    if int(cnum) != int(num):
        new_url = re.sub('list[_\d]*','list_'+str(num),driver.current_url)
        driver.get(new_url)
        locator = (By.XPATH, '//ul[@class="item lh jt_dott f14"]/li[1]/a[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='item lh jt_dott f14']/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.yizheng.gov.cn" + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pagination_index_last']")
    txt = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    total_page = int(re.findall('共 (\d+) 页',txt)[0])
    driver.quit()
    return total_page


data = [

    ["gcjs_zhaobiao_gg", "http://www.yizheng.gov.cn/yzggzyjy/zbgg/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://www.yizheng.gov.cn/yzggzyjy/zbhxr/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.yizheng.gov.cn/yzggzyjy/zhongbgg/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_zjfb_gg", "http://www.yizheng.gov.cn/yzggzyjy/zjfb/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.yizheng.gov.cn/yzggzyjy/cggg/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.yizheng.gov.cn/yzggzyjy/cgjggg/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg", "http://www.yizheng.gov.cn/yzggzyjy/yyhccg/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省仪征市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "yizheng"]
    work(conp)
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     print(d[1])
    #     for i in range(1, total, 10):
    #         df_list = f1(driver, i).values.tolist()
    #         print(df_list[:3])
    #         df1 = random.choice(df_list)
    #         print(f3(driver, df1[2]))
    #
    #     driver.quit()