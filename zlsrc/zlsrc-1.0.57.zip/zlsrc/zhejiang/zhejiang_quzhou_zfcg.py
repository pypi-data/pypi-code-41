import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html





def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//ul[@class='ewb-col-item news-list-items']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='m-pagination-info']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ewb-col-item news-list-items']/li[last()]//a").get_attribute('href')[-30:]
        if 'trade.html' in url:
            s = "/%d.html" % (num) if num > 1 else "/trade.html"
            url = re.sub("/trade\.html", s, url)
        if num == 1:
            url = re.sub("/[0-9]+\.html", "/trade.html", url)
        else:
            s = "/%d.html" % (num) if num > 1 else "/trade.html"
            url = re.sub("/[0-9]+\.html", s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='ewb-col-item news-list-items']/li[last()]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_='ewb-col-item news-list-items')
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            name = a['title'].strip()
        except:
            name = a.text.strip()

        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = "http://www.qzggzy.com" + link.strip()
        td = tr.find("span", class_="ewb-col-date").text
        tmp = [name, td.strip(), href]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='ewb-col-item news-list-items']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='m-pagination-info']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-content'][string-length()>50]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.1)
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
    div = soup.find('div', class_='ewb-main-content')

    return div



data = [
    #
    ["zfcg_zhaobiao_gg", "http://www.qzggzy.com/jyxx/002002/002002001/trade.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],#
    ["zfcg_zhongbiao_gg", "http://www.qzggzy.com/jyxx/002002/002002002/trade.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],#
    ["zfcg_hetong_gg", "http://www.qzggzy.com/jyxx/002002/002002003/trade.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],#
    ["zfcg_gqita_zhao_bian_1_gg", "http://www.qzggzy.com/jyxx/002002/002002004/trade.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],#
    ["zfcg_gqita_zhao_bian_2_gg", "http://www.qzggzy.com/jyxx/002002/002002005/trade.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="浙江省衢州市", **arg)
    est_html(conp, f=f3, **arg)

# 修改日期：2019/8/3
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "zhejiang_quzhou"],num=2)
    # driver = webdriver.Chrome()
    # driver.get("http://www.qzggzy.com/jyxx/002002/002002001/1.html")
    # for i in range(1,4):
    #     f1(driver,i)
