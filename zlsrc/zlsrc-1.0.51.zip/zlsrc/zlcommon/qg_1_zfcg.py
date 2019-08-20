import re
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time



def f1(driver, num):
    locator = (By.XPATH, "//strong[@class='current']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    locator = (By.XPATH, "//ul[@class='lby-list']/li[1]/a|//table[@class='news']/tbody/tr[not(contains(string(.),'项目名称'))][1]/td/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-10:]

    if int(cnum) != int(num):
        new_url = re.sub('page=\d+','page='+str(num),driver.current_url)
        driver.get(new_url)

        locator = (By.XPATH, '//ul[@class="lby-list"]/li[1]/a[not(contains(@href,"%s"))]|//table[@class="news"]/tbody/tr[not(contains(string(.),"项目名称"))][1]/td/a[not(contains(@href,"%s"))]'%(val,val))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="lby-list"]/li[not(@style)]|//table[@class="news"]/tbody/tr[not(contains(string(.),"项目名称"))]')

    data = []
    for content in content_list:

        name = content.xpath("./a/@title|./td/a/text()")[0].strip()
        url = 'http://www.zycg.cn' + content.xpath("./a/@href|./td/a/@href")[0].strip()
        ggstart_time = content.xpath("./span/text()|./td[3]/text()")[0].strip().strip('[').strip(']')

        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="pagination"]/a[last()-1]')
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(total_page)



def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//div[@class="pages_content"][string-length()>50]')
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        locator = (By.XPATH, '//div[@id="edui1_iframeholder"]')
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))
        page1 = driver.page_source
        soup1 = BeautifulSoup(page1, 'html.parser')
        div1 = soup1.find('div', class_='article-colum')
        flag = 0
        if 'id="ueditor_0"' in str(driver.page_source):
            driver.switch_to.frame('ueditor_0')
            locator = (By.XPATH, '//body[@class="view"]/p[string-length()>10]')
            WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))
            flag = 1
    except:
        locator = (By.XPATH, '//table[@class="detail_gg"]/tbody/tr[string-length()>20]')
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        flag = 2

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

    if flag == 1:
        div2 = soup.find('body', class_='view')
        if div2 == None: raise ValueError
        div = str(div1) + str(div2)
        div = BeautifulSoup(div, 'html.parser')
    elif flag == 2:
        div = soup.find('table', class_='detail_gg').parent
    else:raise ValueError


    return div



data = [
    ["zfcg_yucai_gg",
     "http://www.zycg.cn/article/llist?catalog=zqyjgg&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://www.zycg.cn/article/llist?catalog=StockAffiche&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.zycg.cn/article/llist?catalog=ZhongBiao&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.zycg.cn/article/llist?catalog=bggg&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://www.zycg.cn/article/llist?catalog=fbgg&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://www.zycg.cn/article/wsjjxq_list?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"网上竞价"}), f2],

    ["zfcg_zhongbiao_wsjj_gg",
     "http://www.zycg.cn/article/wsjjcj_list?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"网上竞价"}), f2],

    ["zfcg_liubiao_wsjj_gg",
     "http://www.zycg.cn/article/llist?catalog=wsjjfbgg&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"网上竞价"}), f2],

    ["zfcg_kaibiao_gg",
     "http://www.zycg.cn/home/jqkbxm?catalog=StockAffiche&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中央政府采购网", **args)
    est_html(conp, f=f3, **args)

# 修改时间：2019/8/19
if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qg_1_zfcg"]
    work(conp, ipNum=0)

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
    #         print(f)
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://www.zycg.cn/article/show/115437')
    # print(df)



# from anbang_getip import get_ip_proxy
#
#
# print(get_ip_proxy())
