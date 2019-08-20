import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import est_tbs, est_meta, est_html, add_info




def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-news-items']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//li[@class="ewb-page-li current"]').text
    url = driver.current_url
    if int(cnum) != int(num):
        val = driver.find_element_by_xpath("//ul[@class='ewb-news-items']/li[last()]/a").get_attribute('href')[-30:]
        url = re.sub('/[0-9]+\.html', '/%d.html' % num, url)
        driver.get(url)
        # 第二个等待
        locator = (By.XPATH, '//ul[@class="ewb-news-items"]/li[last()]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='ewb-news-items')
    lis = div.find_all('li')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('span', class_='ewb-ndate').get_text(strip=True)
        if 'http' in href:
            href = href
        else:
            href = 'http://www.hbggzy.cn' + href
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='ewb-news-items']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//span[@id="index"]').text.strip()
    num = re.findall(r'/(\d+)', total)[0]
    driver.quit()
    return int(num)





def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="news-article-para"][string-length()>60]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
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
    div = soup.find('div', class_='news-article')
    if div == None:
        raise ValueError('div is None')
    return div


data = [
    ["gcjs_gqita_zhuce_gg", "http://www.hbggzy.cn/jydt/003001/003001001/1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gglx":"项目注册"}), f2],

    ["gcjs_zhaobiao_gg", "http://www.hbggzy.cn/jydt/003001/003001002/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_liu_cheng_gg", "http://www.hbggzy.cn/jydt/003001/003001003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://www.hbggzy.cn/jydt/003001/003001004/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.hbggzy.cn/jydt/003001/003001005/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_hubei_hubei1"], total=2, headless=True, num=1)

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
    #     df=f1(driver, 4)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)

