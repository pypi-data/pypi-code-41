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
from zlsrc.util.etl import est_html, est_meta, add_info




def f1(driver, num):
    locator = (By.XPATH, "//div[@class='liebiao']/ul/li[last()]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//li[@class='thisclass']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='liebiao']/ul/li[last()]//a").get_attribute('href')[-20:]

        Select(driver.find_element_by_xpath("//select[@name='sldd']")).select_by_visible_text('%d'% num)

        locator = (By.XPATH, "//div[@class='liebiao']/ul/li[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='liebiao').ul
    lis = div.find_all('li', recursive=False)
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='sj').text.strip('"')
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.xibutouzi.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df




def f2(driver):
    locator = (By.XPATH, "//div[@class='liebiao']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        num = driver.find_element_by_xpath("//span[@class='pageinfo']/strong[1]").text.strip()
    except:num =1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='gongsiyewu_1'][string-length()>60]")
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
    div = soup.find('div', class_='gongsiyewu_1')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.xibutouzi.com/zhaobiaogonggao/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bian_cheng_gg",
     "http://www.xibutouzi.com/kaibiaoxinxi/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.xibutouzi.com/zhongbiaogonggao/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zgysjg_gg",
     "http://www.xibutouzi.com/a/zigeyushenjieguogongshi/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


# 兰州西部投资咨询有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="甘肃省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest", "gansu_gansusheng_daili"],add_ip_flag=True)


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 3)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


