import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, est_meta


def f1(driver, num):
    locator = (By.XPATH, "//div[@id='list_right']//div[@class='cztt_two_list_left']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//div[@id='list_right']//div[@class='cztt_two_list_left']/div/font")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@id='list_right']//div[@class='cztt_two_list_left']/ul/li[last()]//a").get_attribute('href')[-12:]
        url = re.sub('p=[0-9]+','p=%d'%num, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@id='list_right']//div[@class='cztt_two_list_left']/ul/li[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', id='list_right')
    div = table.find('div', class_='cztt_two_list_left').ul
    trs = div.find_all('li', recursive=False)
    for tr in trs:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span').text.strip()
        ggstart_time = re.findall(r'\[(.*)\]', ggstart_time)[0]
        href = 'http://zjj.shangluo.gov.cn'+a['href']

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@id='list_right']//div[@class='cztt_two_list_left']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@id='list_right']//div[@class='cztt_two_list_left']/div")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'\d+', txt)[1]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='neirong'][string-length()>100]")
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
    div = soup.find('div', id='neirong')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://zjj.shangluo.gov.cn/list.php?cid=7&p=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省商洛市", **args)
    est_html(conp, f=f3, **args)

# 网站加载慢
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_shanxi_shangluo"])


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
    #         d = f3(driver, f)
    #         print(d)


