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
    locator = (By.XPATH, "//div[@id='right']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//td[@class='yahei redfont']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@id='right']/ul/li[last()]/a").get_attribute('href')[-30:]
        url = re.sub('Paging=[0-9]+','Paging=%d'%num, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@id='right']/ul/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', id='right').ul
    lis = table.find_all('li', class_="clearfix")
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='r').text.strip()
        href = 'http://hc.xgsggzy.com'+a['href']
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@id='right']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', total_page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//td[contains(@id, 'TDContent')][string-length()>200] | //td[contains(@id, 'TDContent')]/img")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    except:
        locator = (
        By.XPATH, "//td[contains(@id, 'TDContent')][string-length()>40] | //td[contains(@id, 'TDContent')]/img")
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('table', id=re.compile('^tblInfo'))
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://hc.xgsggzy.com/hcweb/jyxx/004001/004001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_cheng_gg",
     "http://hc.xgsggzy.com/hcweb/jyxx/004001/004001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_kongzhijia_gg",
     "http://hc.xgsggzy.com/hcweb/jyxx/004001/004001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1,  f2],

    ["gcjs_zhongbiaohx_gg",
     "http://hc.xgsggzy.com/hcweb/jyxx/004001/004001004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1,  f2],
    # ####
    ["gcjs_zhongbiao_gg",
     "http://hc.xgsggzy.com/hcweb/jyxx/004001/004001005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ####
    ["zfcg_zhaobiao_gg",
     "http://hc.xgsggzy.com/hcweb/jyxx/004002/004002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_cheng_gg",
     "http://hc.xgsggzy.com/hcweb/jyxx/004002/004002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_gg",
     "http://hc.xgsggzy.com/hcweb/jyxx/004002/004002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省汉川市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_hubei_hanchuan"])


    # for d in data[2:]:
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
    # driver = webdriver.Chrome()
    # d = f3(driver, 'http://hc.xgsggzy.com/hcweb/infodetail/?infoid=378bae8d-8192-424f-969b-0701f286f32b&categoryNum=00400100')
    # print(d)

