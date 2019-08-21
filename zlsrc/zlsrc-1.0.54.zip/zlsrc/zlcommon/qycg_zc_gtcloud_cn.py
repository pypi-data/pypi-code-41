import json
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large



def f1(driver, num):
    url = driver.current_url
    if 'BidAnnouncement.aspx' in url:
        locator = (
        By.XPATH, "//table[contains(@id, 'DXMainTable')]/tbody/tr[contains(@id, 'DXDataRow')][last()]/td[@class='dxgv'][last()-2]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    else:
        locator = (By.XPATH, "//table[contains(@id, 'DXMainTable')]/tbody/tr[contains(@id, 'DXDataRow')][last()]/td[3]//a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//a[@class='cur']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        if 'BidAnnouncement.aspx' in url:
            val = driver.find_element_by_xpath(
                "//table[contains(@id, 'DXMainTable')]/tbody/tr[contains(@id, 'DXDataRow')][last()]/td[@class='dxgv'][last()-2]").text.strip()
        else:
            val = driver.find_element_by_xpath("//table[contains(@id, 'DXMainTable')]/tbody/tr[contains(@id, 'DXDataRow')][last()]/td[3]//a").get_attribute('href')[-30:]
        driver.find_element_by_xpath("//input[@class='uipagenum']").clear()
        driver.find_element_by_xpath("//input[@class='uipagenum']").send_keys(num)
        driver.find_element_by_xpath("//input[@class='jump']").click()
        if 'BidAnnouncement.aspx' in url:
            locator = (By.XPATH,
                       "//table[contains(@id, 'DXMainTable')]/tbody/tr[contains(@id, 'DXDataRow')][last()]/td[@class='dxgv'][last()-2][not(contains(string(), '%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        else:
            locator = (By.XPATH, "//table[contains(@id, 'DXMainTable')]/tbody/tr[contains(@id, 'DXDataRow')][last()]/td[3]//a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", id=re.compile('DXMainTable')).tbody
    lis = div.find_all('tr', id=re.compile('DXDataRow'))
    data = []
    if 'BidAnnouncement.aspx' in url:
        for li in lis:
            try:
                title = li.find_all("td", class_='dxgv')[-3].nobr['title']
            except:
                title = li.find_all("td", class_='dxgv')[-3].nobr.text.strip()
            ggstart_time = li.find_all("td", class_='dxgv')[-1].text.strip()
            href = '-'
            info = {}
            zbdw = li.find_all("td", class_='dxgv')[-2].nobr['title']
            if zbdw: info['zbdw'] = zbdw

            if info:
                info = json.dumps(info, ensure_ascii=False)
            else:
                info = None
            tmp = [title, ggstart_time, href, info]
            data.append(tmp)
    else:
        for li in lis:
            a = li.find("a")
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            ggstart_time = li.find_all("td", class_='dxgv')[-4].text.strip()
            link = a["href"]
            if 'http' in link:
                href = link
            else:
                href = 'http://zc.gtcloud.cn/HomePage/' + link
            info = {}

            end_time = li.find_all("td", class_='dxgv')[-3].text.strip()
            if end_time:info['end_time']=end_time
            cglx = li.find_all("td", class_='dxgv')[-2].text.strip()
            if cglx:info['cglx']=cglx

            if info:info = json.dumps(info, ensure_ascii=False)
            else:info = None
            tmp = [title, ggstart_time, href, info]
            data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    url = driver.current_url
    if 'BidAnnouncement.aspx' in url:
        locator = (
        By.XPATH, "//table[contains(@id, 'DXMainTable')]/tbody/tr[contains(@id, 'DXDataRow')][last()]/td[@class='dxgv'][last()-2]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    else:
        locator = (By.XPATH, "//table[contains(@id, 'DXMainTable')]/tbody/tr[contains(@id, 'DXDataRow')][last()]/td[3]//a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@class='count']")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='table'][string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('table', class_='table')
    return div


data = [

    #
    ["qycg_zhaobiao_gg",
     "http://zc.gtcloud.cn/HomePage/TenderNotice.aspx",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    #
    ["qycg_zhongbiao_gg",
     "http://zc.gtcloud.cn/HomePage/BidAnnouncement.aspx",
     ["name", "ggstart_time", "href", "info"],f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="绿城集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "zc_gtcloud_cn"])

    #
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
    #     df=f1(driver, 11)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


