import json
import random
import re
import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from zlsrc.util.fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta,est_meta_large
import time
from selenium import webdriver




def f1(driver, num):
    new_url = re.sub('page=\d+', 'page=' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, "//form[@id='moderate']/li")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//form[@id='moderate']/li")
    for content in content_list:
        name = content.xpath("./a/span/text()")[0].strip()
        ggstart_time = content.xpath("./a/em/text()")[0].strip()
        url = 'http://www.crecgec.com/' + content.xpath('./a/@href')[0].strip()
        info_temp = {}
        try:
            area = content.xpath("./a/strong[@class='adress' or @class='qy']/text()")[0].strip()
            info_temp = {'area':area}
        except:
            pass
        danwei = content.xpath("./a/strong[@class='comp' or @class='dw']/text()")[0].strip()
        info_temp.update({'danwei': danwei})
        info = json.dumps(info_temp, ensure_ascii=False)
        temp = [name, ggstart_time, url, info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):   # 求总页数
    locator = (By.XPATH,"//div[@class='pg']/label/span")
    href_temp = WebDriverWait(driver,20).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('\d+', href_temp)[0]  #把总页数截取出来
    # print(total_page)
    driver.quit()
    return int(total_page)



#http://www.crecgec.com/article-156723-1-1.html  #详情页

def f3(driver, url):   #定位详情页的内容
    driver.get(url)
    locator = (By.XPATH, "//div[@class='pagemain']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='pagemain')
    if '404-页面未找到' in div:
        return '404-页面未找到'
    return div




# http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=12&sortid=12&filter=sortid&page=3  #招标公告

# http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=13&filter=sortid&sortid=13&page=3  # 中标告示

#http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=16&filter=sortid&sortid=16&page=3    #澄清补遗

data = [
    ["qycg_zhaobiao_gg",
     "http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=12&sortid=12&filter=sortid&page=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_gqita_bu_gg",
     "http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=16&filter=sortid&sortid=16&page=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiaohx_gg",
     "http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=13&filter=sortid&sortid=13&page=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]
#####中铁鲁班网
def work(conp, **args):
    est_meta(conp, data=data, diqu="中铁鲁班商务网", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "qycg_www_crecgec_com"]
    work(conp,total=100)


    # for d in data:
    #     # print(d[1])
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print('total_page',total)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     for i in range(1,total,300):
    #         df = f1(driver,i)
    #         item_list = df.values.tolist()
    #         print(item_list)
    #         print(str(f3(driver, item_list[0][2]))[:100])
    #         driver.get(d[1])
    #     driver.quit()

    # url = 'http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=12&sortid=12&filter=sortid&page=3'
    # driver= webdriver.Chrome()
    # driver.get(url)
    # f1(driver,1)

