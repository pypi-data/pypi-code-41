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
from zlsrc.util.etl import est_html, est_meta




def f1(driver, num):
    locator = (By.XPATH, "//table[@class='n_new_zi']/tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//div[@class='xiaocms-page']/span")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//table[@class='n_new_zi']/tbody/tr[1]//a").get_attribute('href')[-10:]

        url = re.sub(r'page=[0-9]+', 'page=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//table[@class='n_new_zi']/tbody/tr[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('table', class_='n_new_zi').tbody
    divs = lis.find_all('tr', recursive=False)
    for tr in divs[:-2:2]:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span').text.strip()
        ggstart_time = re.findall(r'[0-9]{4}-[0-9]{,2}-[0-9]{,2}', ggstart_time)[0]
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.sdqixin.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@class='n_new_zi']/tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='xiaocms-page']/a[last()]")
    page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')
    num = re.findall(r'page=([0-9]+)', page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='rt n_about_n'][string-length()>60]")
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
    div = soup.find('div', class_=re.compile('n_about_n'))
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.sdqixin.com/index.php?catid=44&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["jqita_zhongbiao_gg",
     "http://www.sdqixin.com/index.php?catid=45&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 山东齐信招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_sdqixin_com"])


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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


