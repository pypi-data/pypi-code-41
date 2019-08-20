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


total_num = None

def f1(driver, num):
    locator = (By.XPATH, "//div[@class='class_r_list']/table/tbody/tr[@height='40'][last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//td[contains(@id, 'fanye')]")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', total_page)[0]
    # print(cnum)

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='class_r_list']/table/tbody/tr[@height='40'][last()]//a").get_attribute('href')[-12:]
        if 'zbtb.htm' in url:
            s = 'zbtb/%d.htm'% int(total_num-num+1) if num>1 else 'zbtb.htm'
            url = re.sub('zbtb\.htm', s, url)
        elif num == 1:
            re.sub('zbtb/[0-9]+\.htm', 'zbtb.htm', url)
        else:
            s = 'zbtb/%d.htm' % int(total_num - num + 1) if num > 1 else 'zbtb.htm'
            re.sub('zbtb/[0-9]+\.htm', s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='class_r_list']/table/tbody/tr[@height='40'][last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    time.sleep(1)
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='class_r_list').table.tbody
    lis = table.find_all('tr', height='40')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_=re.compile('timestyle')).text.strip()
        href = 'http://www.xjbl.gov.cn/'+a['href'].split('../')[-1]

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    global total_num
    locator = (By.XPATH, "//div[@class='class_r_list']/table/tbody/tr[@height='40'][last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[contains(@id, 'fanye')]")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    total_num = int(re.findall(r'/(\d+)', total_page)[0])
    driver.quit()
    return total_num



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@class, 'news_content')][string-length()>100]")
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
    div = soup.find('div', class_='news_content').parent
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.xjbl.gov.cn/zdlygk/zbtb.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="内蒙古自治区博乐市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_xinjiang_bole"])


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


