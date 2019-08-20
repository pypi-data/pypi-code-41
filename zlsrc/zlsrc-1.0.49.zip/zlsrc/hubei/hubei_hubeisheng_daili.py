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
    locator = (By.XPATH, "//div[@class='noticeList1']/ul/li[last()]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//div[@class='page']/a[contains(@class, 'on')]")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='noticeList1']/ul/li[last()]/a").get_attribute('href')[-10:]

        url = re.sub(r'page=[0-9]+', 'page=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='noticeList1']/ul/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='noticeList1').ul
    lis = div.find_all('li', recursive=False)
    for tr in lis:
        a = tr.find('a')
        try:
            name = a.h5['title']
        except:
            name = a.h5.text.strip()
        ggstart_time = tr.find('span').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.hbbidding.com.cn' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='noticeList1']/ul/li[last()]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='page']/a[last()-1]")
    num = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='noticeWrap passageWrap'][string-length()>100]")
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
    div = soup.find('div', class_='noticeWrap passageWrap')
    if div == None:
        raise ValueError
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.hbbidding.com.cn/list/19.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://www.hbbidding.com.cn/list/17.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_huowu_gg",
     "http://www.hbbidding.com.cn/list/20.html?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'货物招标'}), f2],

    ["jqita_zhaobiao_fuwu_gg",
     "http://www.hbbidding.com.cn/list/21.html?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'服务招标'}), f2],

    ["jqita_zhaobiao_guoji_gg",
     "http://www.hbbidding.com.cn/list/18.html?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'国际招标'}), f2],

    ["jqita_gqita_bian_cheng_gg",
     "http://www.hbbidding.com.cn/list/46.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.hbbidding.com.cn/list/25.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.hbbidding.com.cn/list/23.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_huowu_gg",
     "http://www.hbbidding.com.cn/list/26.html?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '货物招标'}), f2],

    ["jqita_zhongbiao_fuwu_gg",
     "http://www.hbbidding.com.cn/list/27.html?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '服务招标'}), f2],

    ["jqita_zhongbiao_guoji_gg",
     "http://www.hbbidding.com.cn/list/24.html?page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '国际招标'}), f2],
]

# 湖北省招标股份有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "qycg_www_hbbidding_com_cn"])


    # for d in data[-6:]:
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
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


