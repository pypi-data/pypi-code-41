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
    locator = (By.XPATH, "//ul[@class='dtlist']/dl[last()]/dd/h5/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    try:
        locator = (By.XPATH, "//div[@class='uls fr']/a[@class='cur']")
        page = WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(page)
    except:cnum=1

    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='dtlist']/dl[last()]/dd/h5/a").get_attribute('href')[-20:]

        url = re.sub(r'-[0-9]+\.htm', '-%d.htm' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='dtlist']/dl[last()]/dd/h5/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='dtlist')
    lis = div.find_all('dl', class_='nrtop', recursive=False)
    for tr in lis:
        a = tr.find('h5').a
        try:
            name = a['title']
        except:
            name = a.text.strip()

        ggstart_time = '-'
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.fzjtcn.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='dtlist']/dl[last()]/dd/h5/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pagingNav']/p")
        page = WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'共(\d+)页', page)[0]
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//div[@id='cntrBody'][string-length()>100]")
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
    div = soup.find('div', class_='left2')
    if div == None:
        raise ValueError
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.fzjtcn.com/zbgg-1.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bian_cheng_gg",
     "http://www.fzjtcn.com/cqdy-1.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.fzjtcn.com/zbgs-1.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

#法正项目管理集团有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="法正项目管理集团有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_fzjtcn_com"])

    #
    # for d in data[1:]:
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


