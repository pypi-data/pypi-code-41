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
    locator = (By.XPATH, "//div[@class='c1-body']/div[last()]//a[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//div[@class='pagination']")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(re.findall(r'(\d+)/', page)[0])

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='c1-body']/div[last()]//a[last()]").get_attribute('href')[-15:]
        Select(driver.find_element_by_xpath("//div[@class='pagination']/select")).select_by_visible_text('%d'% num)
        time.sleep(1)

        locator = (By.XPATH, "//div[@class='c1-body']/div[last()]//a[last()][not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='c1-body')
    lis = table.find_all('div', class_='c1-bline')
    for tr in lis:
        a = tr.find_all('a')[-1]
        try:
            name = a['title']
        except:
            name = a.text.strip()

        ggstart_time = tr.find('div', class_='gray f-right').text.strip()

        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.hnwxzb.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='c1-body']/div[last()]//a[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='pagination']")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='page_newscontent']")
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
    div = soup.find('div', class_='page_newscontent').parent
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gc_gg",
     "http://www.hnwxzb.com/goodsCenter2.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'工程招标'}), f2],

    ["jqita_biangeng_gc_gg",
     "http://www.hnwxzb.com/goodsCenter3.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '工程招标'}), f2],

    ["jqita_zhongbiao_gc_gg",
     "http://www.hnwxzb.com/goodsCenter4.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '工程招标'}), f2],
    ###
    ["jqita_zhaobiao_hw_gg",
     "http://www.hnwxzb.com/goodsInternationalCenter2.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'货物招标'}), f2],

    ["jqita_biangeng_hw_gg",
     "http://www.hnwxzb.com/goodsInternationalCenter3.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '货物招标'}), f2],

    ["jqita_zhongbiao_hw_gg",
     "http://www.hnwxzb.com/goodsInternationalCenter4.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '货物招标'}), f2],
    ###
    ["jqita_zhaobiao_fw_gg",
     "http://www.hnwxzb.com/projectCenter2.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '服务招标'}), f2],

    ["jqita_biangeng_fw_gg",
     "http://www.hnwxzb.com/projectCenter3.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '服务招标'}), f2],

    ["jqita_zhongbiao_fw_gg",
     "http://www.hnwxzb.com/projectCenter4.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '服务招标'}), f2],
    ###
    ["jqita_zhaobiao_gj_gg",
     "http://www.hnwxzb.com/otherCenter2.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '国际招标'}), f2],


    ["jqita_zhongbiao_gj_gg",
     "http://www.hnwxzb.com/otherCenter4.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '国际招标'}), f2],
]


# 河南省伟信招标管理咨询有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="河南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_hnwxzb_com"], )

    #
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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


