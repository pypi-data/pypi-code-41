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
    locator = (By.XPATH, "//div[@class='list-group']/a[last()]")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//li[@class='active']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)
    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='list-group']/a[last()]").get_attribute('href')[-30:]
        url = re.sub('pageindex=[0-9]+', 'pageindex=%d' % (num-1), driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='list-group']/a[last()][not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='col-md-12').div
    lis = table.find_all('a')
    for tr in lis:
        ggstart_time = tr.label.extract().text.strip()
        name = tr.text.strip().replace(" ", '')
        link = tr['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.gxbidding.com' + link
        info = {}
        if re.findall('\[(\w+?)\]', name):
            zblx = re.findall('\[(\w+?)\]', name)[0]
            info['zblx']=zblx

        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='list-group']/a[last()]")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath("//ul[@class='pagination']/li[last()]/a").get_attribute('href')
    num = int(re.findall(r'pageindex=(\d+)', total)[0])+1

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='panel-body'][string-length()>60] | //div[@class='panel-body']/img")
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
    div = soup.find('div', id='PrintArea')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_gqita_zbyugao_gg",
     "http://www.gxbidding.com/Home/AnnouncementList?typecode=ZBYG&pageindex=0",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'招标预告'}), f2],

    ["jqita_zhaobiao_gg",
     "http://www.gxbidding.com/Home/AnnouncementList?typecode=ZBGG&pageindex=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_kongzhijia_gg",
     "http://www.gxbidding.com/Home/AnnouncementList?typecode=KZJGG&pageindex=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_dayi_gg",
     "http://www.gxbidding.com/Home/AnnouncementList?typecode=DYGG&pageindex=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_biangeng_gg",
     "http://www.gxbidding.com/Home/AnnouncementList?typecode=BGGG&pageindex=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.gxbidding.com/Home/AnnouncementList?typecode=JGGS&pageindex=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.gxbidding.com/Home/AnnouncementList?typecode=JGGG&pageindex=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

# 广西招标采购网
def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_guangxi_guangxisheng_daili"], )


    # for d in data[1:]:
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


