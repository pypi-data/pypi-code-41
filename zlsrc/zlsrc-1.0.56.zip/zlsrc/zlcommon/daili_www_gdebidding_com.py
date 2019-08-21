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
    locator = (By.XPATH, "//div[@class='padding-big']/div[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//div[@class='padding-big']/div[last()]/div")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(re.findall(r'(\d+)/', snum)[0])

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='padding-big']/div[1]/a").get_attribute('href')[-12:]

        Select(driver.find_element_by_xpath("//div[@class='padding-big']/div[last()]/div/select")).select_by_value("{}".format(num))
        time.sleep(1)

        locator = (By.XPATH, "//div[@class='padding-big']/div[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('div', class_='padding-big')
    divs = lis.find_all('div', recursive=False)
    for tr in divs[:-1]:
        a = tr.find('a')
        if a.find('span'):
            a.find('span').extract()
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='float-right').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'https://www.gdebidding.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='padding-big']/div[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='padding-big']/div[last()]/div")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    page = re.findall(r'/(\d+)页', total_page)[0]
    driver.quit()
    return int(page)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='padding-big'][string-length()>60]")
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
    div = soup.find('div', class_='padding-big')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "https://www.gdebidding.com/zbxxgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_biangeng_gg",
     "https://www.gdebidding.com/cqgzgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_zhongbiaohx_gg",
     "https://www.gdebidding.com/zbjggs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_zhongbiao_gg",
     "https://www.gdebidding.com/zbjggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zgys_gg",
     "https://www.gdebidding.com/zgysgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_zbyg_gg",
     "https://www.gdebidding.com/zbyg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'招标信息预告'}), f2],

    ["jqita_gqita_wlpt_gg",
     "https://www.gdebidding.com/wbptljzb/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '外联平台信息'}), f2],

    ["jqita_zhaobiao_wsjj_gg",
     "https://www.gdebidding.com/cgxxgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '网上竞价'}), f2],

    ["jqita_zhongbiao_wsjj_gg",
     "https://www.gdebidding.com/cgjggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '网上竞价'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省机电设备招标中心有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_gdebidding_com"])


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


