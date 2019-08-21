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

# jqita_gqita_zhao_zhong_gg      #模式名
# http://www.sddyxg.com/nr.jsp   # 翻页前
# http://www.sddyxg.com/nr.jsp   # 翻页后

def f1(driver, num):
    new_url = re.sub('pageno=\d+', 'pageno=' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, "//div[@id='newsList31']/div[@topclassname]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    data = []
    info_temp = {}
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@id='newsList31']/div[@topclassname]")
    for content in content_list:
        ggtype_tmp = content.xpath('./table/tbody/tr[count(td)=4]')
        if ggtype_tmp != []:
            ggtype = ggtype_tmp[0].xpath('./td[3]/a/text()')[0].strip('[]').strip()
            info_temp.update({'ggtype':ggtype})
        name = content.xpath("./table//td[2]/a/text()")[0].strip()
        ggstart_time = content.xpath("./table//td[last()]/a/text()")[0].strip()
        url = 'http://www.sddyxg.com/' + content.xpath("./table//td[2]/a/@href")[0].strip()
        info = json.dumps(info_temp,ensure_ascii=False)
        temp = [name, ggstart_time, url,info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):   # 求总页数
    locator = (By.XPATH,"//div[@id='pagenation31']/div[last()-1]/a/span")
    total_page = WebDriverWait(driver,20).until(EC.presence_of_element_located(locator)).text   #把总页数截取出来
    # print(total_page)
    driver.quit()
    return int(total_page)


#http://www.sddyxg.com/nd.jsp?id=1540&groupId=-1  #详情页
def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@class,'newsDetail')][string-length()>50]")
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
    div = soup.find('div', attrs={'class':re.compile('newsDetail')})
    div.find('div',class_='middlePanel').clear()
    return div

data = [

    ["jqita_gqita_zhao_zhong_gg",
     "http://www.sddyxg.com/nr.jsp?m31pageno=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


######山东东岳项目管理有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "qycg_www_sddyxg_com"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get('http://www.sddyxg.com/nr.jsp?m31pageno=5')
    # f1(driver,1)
    # print(f3(driver, 'http://www.sddyxg.com/nd.jsp?id=1544&groupId=-1'))