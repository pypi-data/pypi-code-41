import json
import random
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
    locator = (By.XPATH, "//ul[@class='textlist']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//span[@class='current']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='textlist']/li[last()]/a").get_attribute('href')[-15:]
        url = re.sub('p=[0-9]+', 'p=%d' % num, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='textlist']/li[last()]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='textlist')
    lis = div.find_all('li')
    for tr in lis:
        a = tr.find('a')
        name = a.text.strip()
        ggstart_time = tr.find('span', class_='float_right').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.czztb.com' + link
        info = {}
        if re.findall('【(.*?)】', name):
            n = len(re.findall('【(.*?)】', name))
            for i in range(int(n)):
                if i == 0:
                    id_num = re.findall('【(.*?)】', name)[0]
                    info['id_num']=id_num
                elif i == 1:
                    zblx = re.findall('【(.*?)】', name)[1]
                    info['zblx']=zblx
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='textlist']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@class='pageinfo']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', total_page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='InfoContent'][string-length()>60]")
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
    div = soup.find('div', class_='InfoContent').parent
    return div


data = [
    ["qycg_zhaobiao_gg",
     "http://www.czztb.com/index.php/zbcggg.html?&p=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qycg_gqita_bian_bu_gg",
     "http://www.czztb.com/index.php/bcgg.html?&p=1",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["qycg_zhongbiao_gg",
     "http://www.czztb.com/index.php/zbgg.html?&p=1",
     ["name", "ggstart_time", "href", "info"],f1 ,f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏中冠工程咨询有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_czztb_com"])


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


