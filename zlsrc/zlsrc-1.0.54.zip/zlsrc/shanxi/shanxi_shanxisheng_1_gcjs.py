import json
import re
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time



def f1(driver, num):
    locator = (By.XPATH, "//div[@class='pagination']/label[2]")
    cnum = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, '//table[@class="table_text"]/tbody/tr[child::td][1]/td[1]/a')
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-15:]

    if int(cnum) != int(num):
        new_url = re.sub('page=\d+', 'page=' + str(num), driver.current_url)

        driver.get(new_url)

        locator = (By.XPATH, '//table[@class="table_text"]/tbody/tr[child::td][1]/td[1]/a[not(contains(@href,"%s"))]' % (val))
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="table_text"]/tbody/tr[child::td]')

    data = []
    for content in content_list:
        name = content.xpath("./td[1]/a/@title")[0].strip()
        info_temp = {}
        url = re.findall('\'([^\']+)', content.xpath("./td[1]/a/@href")[0].strip())[0]
        type = content.xpath("./td[2]/span/@title")[0].strip()

        try:
            area = content.xpath("./td[3]/span/@title")[0].strip()
            info_temp.update({'type': type, 'area': area})
        except:
            area=type
            info_temp.update({'area': area})

        ggstart_time = content.xpath("./td[5]/span/@title|./td[5]/text()")[0].strip()
        from_ = content.xpath("./td[4]/span/@title|./td[4]/text()")[0].strip()
        if ggstart_time != '':
            info_temp.update({'from': from_})
        else:
            ggstart_time = from_
        info = json.dumps(info_temp, ensure_ascii=False)
        temp = [name, ggstart_time, url, info]

        data.append(temp)

    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pagination']/label[1]")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    total_page = 100
    #  只能爬取前100页的内容。
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='mian_list']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='mian_list')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://bulletin.sntba.com/xxfbcmses/search/change.html?searchDate=1994-07-17&dates=300&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgys_gg",
     "http://bulletin.sntba.com/xxfbcmses/search/qualify.html?searchDate=1994-07-17&dates=300&categoryId=92&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://bulletin.sntba.com/xxfbcmses/search/candidate.html?searchDate=1994-07-17&dates=300&categoryId=91&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://bulletin.sntba.com/xxfbcmses/search/candidate.html?searchDate=1994-07-17&dates=300&categoryId=90&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://bulletin.sntba.com/xxfbcmses/search/change.html?searchDate=1994-07-17&dates=300&categoryId=89&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_sntba_com"]
    # driver=webdriver.Chrome()
    # driver.get('http://bulletin.sntba.com/xxfbcmses/search/change.html?searchDate=1994-07-17&dates=300&categoryId=92&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=&page=2')
    # print(f1(driver, 3).values.tolist())
    work(conp,pageloadstrategy='none',pageloadtimeout=120)
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     df_list = f1(driver, i).values.tolist()
    #     # print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
