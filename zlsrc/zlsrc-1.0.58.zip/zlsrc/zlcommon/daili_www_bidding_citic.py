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
    locator = (By.XPATH, "//ul[@class='comstyle newslist-01']/li[@class='content column-num1'][1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//span[@class='current']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='comstyle newslist-01']/li[@class='content column-num1'][1]//a").get_attribute('href')[-15:]

        locator = (By.XPATH, "//div[@class='number']/a[last()]")
        total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('onclick')
        jsq = re.findall(r'jump_(.*)\(', total_page)[0]

        driver.execute_script('jump_{0}({1},10);'.format(jsq, num))

        locator = (By.XPATH, "//ul[@class='comstyle newslist-01']/li[@class='content column-num1'][1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='comstyle newslist-01')
    lis = div.find_all('li', class_='content column-num1')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('li', class_='date').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.bidding.citic' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='number']/a[last()-2]")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(total_page)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='newsdetailshow'][string-length()>40]")
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
    div = soup.find('div', id='newsdetailshow')
    return div


data = [
    ["qycg_zhaobiao_gc_gg",
     "http://www.bidding.citic/news_list2/newsCategoryId=16.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'工程'}),f2],

    ["qycg_zhaobiao_hw_gg",
     "http://www.bidding.citic/news_list2/newsCategoryId=18.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'货物'}),f2],

    ["qycg_zhaobiao_fw_gg",
     "http://www.bidding.citic/news_list2/newsCategoryId=19.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '服务'}),f2],

    ["qycg_biangeng_gg",
     "http://www.bidding.citic/news_list2/newsCategoryId=21.html",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["qycg_gqita_bian_da_gg",
     "http://www.bidding.citic/news_list2/newsCategoryId=22.html",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["qycg_zhongbiao_gg",
     "http://www.bidding.citic/news_list2/newsCategoryId=10.html",
     ["name", "ggstart_time", "href", "info"],f1 ,f2],

]

###中信国际招标有限公司
def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中信国际招标有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_bidding_citic"])

    # 
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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


