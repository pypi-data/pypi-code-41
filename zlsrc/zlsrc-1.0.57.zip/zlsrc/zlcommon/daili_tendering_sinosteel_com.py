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
    locator = (By.XPATH, "//table[@class='mar_t17'][1]/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//table[@class='mar_t17'][2]/tbody//span[@class='f12_red'][1]")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//table[@class='mar_t17'][1]/tbody/tr[last()]/td/a").get_attribute('href')[-20:]
        Select(driver.find_element_by_xpath("//select[@name='selectgoto']")).select_by_visible_text('%d'% num)
        time.sleep(1)

        locator = (By.XPATH, "//table[@class='mar_t17'][1]/tbody/tr[last()]/td/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find_all('table', class_='mar_t17')[0].tbody
    lis = table.find_all('tr')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()

        ggstart_time = tr.find('span', class_='f12_grey_1').text.strip()
        ggstart_time = re.findall(r'\[(.*)\]', ggstart_time)[0]
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://tendering.sinosteel.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@class='mar_t17'][1]/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//table[@class='mar_t17'][2]/tbody//span[@class='f12_red'][last()]")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(page)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='content'][string-length()>30]")
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
    div = soup.find('table', class_='mar_t10')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://tendering.sinosteel.com/zbdt/zbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://tendering.sinosteel.com/zbdt/zbgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_biangeng_gg",
     "http://tendering.sinosteel.com/zbdt/bggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中钢招标有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_tendering_sinosteel_com"], )


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


