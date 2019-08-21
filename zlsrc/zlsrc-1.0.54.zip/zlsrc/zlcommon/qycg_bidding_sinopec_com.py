import random
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='MoreinfoListsearch1_DataGrid1']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//div[@id='MoreinfoListsearch1_Pager']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)', snum)[2]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='MoreinfoListsearch1_DataGrid1']/tbody/tr[last()]//a").get_attribute('href')[-40:]

        driver.execute_script("javascript:__doPostBack('MoreinfoListsearch1$Pager','{}')".format(num))

        locator = (By.XPATH, "//table[@id='MoreinfoListsearch1_DataGrid1']/tbody/tr[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='MoreinfoListsearch1_DataGrid1').tbody
    lis = div.find_all('tr')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('td')[-1].text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'https://bidding.sinopec.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@id='MoreinfoListsearch1_Pager']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'(\d+)', total_page)[1]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo'][string-length()>40]")
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
    div = soup.find('table', id='tblInfo')
    return div


data = [

    ["qycg_zhaobiao_gg",
     "https://bidding.sinopec.com/tpfront/CommonPages/searchmore.aspx?CategoryNum=004001",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qycg_zgys_gg",
     "https://bidding.sinopec.com/tpfront/CommonPages/searchmore.aspx?CategoryNum=004002",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["qycg_zhongbiaohx_gg",
     "https://bidding.sinopec.com/tpfront/CommonPages/searchmore.aspx?CategoryNum=004004",
     ["name", "ggstart_time", "href", "info"],f1 ,f2],

    ["qycg_zhongbiao_gg",
     "https://bidding.sinopec.com/tpfront/CommonPages/searchmore.aspx?CategoryNum=004005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国石化物资招标投标网", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "bidding_sinopec_com"])


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


