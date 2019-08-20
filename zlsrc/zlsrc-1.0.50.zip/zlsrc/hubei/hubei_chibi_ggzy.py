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
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[@class='wb-data-list'][1]/div[@class='wb-data-infor']/a[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//td[@class='yahei redfont']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='wb-data-item']/li[@class='wb-data-list'][1]/div[@class='wb-data-infor']/a[last()]").get_attribute('href')[-40:]
        url = re.sub('Paging=[0-9]+','Paging=%d'%num, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='wb-data-item']/li[@class='wb-data-list'][1]/div[@class='wb-data-infor']/a[last()][not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('ul', class_='wb-data-item')
    lis = table.find_all('li', class_="wb-data-list")
    for tr in lis:
        div = tr.find('div', class_='wb-data-infor')
        a = div.find_all('a')[-1]
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='wb-data-date r').text.strip()
        href = 'http://xnztb.xianning.gov.cn:9001'+a['href']
        info = {}
        if div.find('font', color="red"):
            gglx = div.find('font', color="red").text.strip()
            info['gglx']=gglx
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[@class='wb-data-list'][1]/div[@class='wb-data-infor']/a[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', total_page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@id, 'mainContent')][string-length()>100]")
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
    div = soup.find('div', class_='row')
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://xnztb.xianning.gov.cn:9001/cbweb/showinfo/moreinfolist.aspx?categorynum=005008&Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],
    #
    ["jqita_biangeng_gg",
     "http://xnztb.xianning.gov.cn:9001/cbweb/showinfo/moreinfolist.aspx?categorynum=005009&Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["jqita_zhongbiaohx_gg",
     "http://xnztb.xianning.gov.cn:9001/cbweb/showinfo/moreinfolist.aspx?categorynum=005010&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1,  f2],
    # # ####
    ["jqita_zhongbiao_gg",
     "http://xnztb.xianning.gov.cn:9001/cbweb/showinfo/moreinfolist.aspx?categorynum=005011&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省赤壁市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_hubei_chibi"])


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


