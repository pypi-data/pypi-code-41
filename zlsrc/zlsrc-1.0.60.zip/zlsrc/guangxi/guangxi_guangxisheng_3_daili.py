import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-mechanism-items']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//li[@class='active']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ewb-mechanism-items']/li[last()]//a").get_attribute('href')[-30:]
        driver.find_element_by_xpath("//div[@class='m-pagination-group']/input").clear()
        driver.find_element_by_xpath("//div[@class='m-pagination-group']/input").send_keys(num)
        driver.find_element_by_xpath("//div[@class='m-pagination-group']/button").click()
        locator = (By.XPATH, "//ul[@class='ewb-mechanism-items']/li[last()]//a[not(contains(@href, '%s'))]"% val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    div = soup.find('ul', class_='ewb-mechanism-items')
    lis = div.find_all('li')
    data = []
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('div', class_='r').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.guangxibid.com.cn' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='ewb-mechanism-items']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//ul[@class='m-pagination-page']/li[last()]//a")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-article-info'][string-length()>60]")
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
    div = soup.find('div', class_='ewb-details-info')
    return div


data = [

    ["jqita_zhaobiao_gg",
     "http://www.guangxibid.com.cn/zbcg/002001/list.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["jqita_biangeng_gg",
     "http://www.guangxibid.com.cn/zbcg/002002/list.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.guangxibid.com.cn/zbcg/002003/list.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


##广西建设工程机电设备招标中心有限公司,广西招标网
def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_guangxibid_com_cn"])


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = d[-1](driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=d[-2](driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


